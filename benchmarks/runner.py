import asyncio
import statistics
from dataclasses import dataclass

from rich.progress import Progress, SpinnerColumn, TextColumn

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URI, DB_NAME, ITERATIONS
from db import get_pymongo_db, connect_mongoengine, disconnect_mongoengine
from models.beanie_models import CategoryDoc, OrderDoc
from benchmarks.registry import BenchmarkInfo, Library, OpType, get_benchmarks
from benchmarks.timer import sync_timer, AsyncTimer


@dataclass
class BenchmarkResult:
    benchmark: BenchmarkInfo
    timings: list[float]
    median_ms: float
    min_ms: float
    max_ms: float
    p95_ms: float
    mean_ms: float


def _compute_stats(bm: BenchmarkInfo, timings: list[float]) -> BenchmarkResult:
    ms = [t * 1000 for t in timings]
    sorted_ms = sorted(ms)
    p95_idx = min(int(len(sorted_ms) * 0.95), len(sorted_ms) - 1)
    return BenchmarkResult(
        benchmark=bm,
        timings=timings,
        median_ms=statistics.median(ms),
        min_ms=min(ms),
        max_ms=max(ms),
        p95_ms=sorted_ms[p95_idx],
        mean_ms=statistics.mean(ms),
    )


def preselect_targets(db) -> dict:
    """Pick random query targets that all libraries will use."""
    sample_cat = db.categories.aggregate([{"$sample": {"size": 1}}]).next()
    sample_order = db.orders.aggregate([{"$sample": {"size": 1}}]).next()

    # Find status with most documents for bulk reads
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    best_status = next(db.orders.aggregate(pipeline))["_id"]

    return {
        "category_slug": sample_cat["slug"],
        "order_number": sample_order["order_number"],
        "bulk_status": best_status,
    }


def run_benchmarks(
    library: Library | None = None,
    op_type: OpType | None = None,
) -> list[BenchmarkResult]:
    # Import benchmark modules to trigger registration
    import raw.reads
    import raw.writes  # noqa: F401
    import dataclasses_raw.reads
    import dataclasses_raw.writes  # noqa: F401
    import beanie_odm.reads
    import beanie_odm.writes  # noqa: F401
    import mongoengine_odm.reads
    import mongoengine_odm.writes  # noqa: F401

    all_bms = get_benchmarks(library=library, op_type=op_type)

    # Pre-select query targets
    db = get_pymongo_db()
    targets = preselect_targets(db)
    ctx = {"db": db, "targets": targets}

    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
    ) as progress:
        # Run reads first, then writes
        reads = [b for b in all_bms if b.op_type == OpType.READ]
        writes = [b for b in all_bms if b.op_type == OpType.WRITE]

        # --- Sync benchmarks (raw + mongoengine) ---
        sync_reads = [b for b in reads if not b.is_async]
        sync_writes = [b for b in writes if not b.is_async]

        if any(b.library == Library.MONGOENGINE for b in sync_reads + sync_writes):
            connect_mongoengine()

        for bm in sync_reads + sync_writes:
            task = progress.add_task(f"{bm.library.value}: {bm.name}", total=None)
            timings = _run_sync_benchmark(bm, ctx)
            results.append(_compute_stats(bm, timings))
            progress.update(
                task,
                completed=True,
                description=f"[green]{bm.library.value}: {bm.name}",
            )
            progress.stop_task(task)

        if any(b.library == Library.MONGOENGINE for b in sync_reads + sync_writes):
            disconnect_mongoengine()

        # Cleanup write benchmark docs (sync)
        db.categories.delete_many({"_benchmark": True})
        db.orders.delete_many({"_benchmark": True})

        # --- Async benchmarks (beanie) ---
        async_reads = [b for b in reads if b.is_async]
        async_writes = [b for b in writes if b.is_async]

        if async_reads or async_writes:
            async_results = asyncio.run(
                _run_all_async_benchmarks(async_reads + async_writes, ctx, progress)
            )
            results.extend(async_results)

            # Cleanup write benchmark docs (async inserts went to same collections)
            db.categories.delete_many({"_benchmark": True})
            db.orders.delete_many({"_benchmark": True})

    return results


def _run_sync_benchmark(bm: BenchmarkInfo, ctx: dict) -> list[float]:
    timings = []
    for _ in range(ITERATIONS):
        with sync_timer() as t:
            bm.func(ctx)
        timings.append(t.elapsed_seconds)
    return timings


async def _run_all_async_benchmarks(
    benchmarks: list[BenchmarkInfo],
    ctx: dict,
    progress: Progress,
) -> list[BenchmarkResult]:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    await init_beanie(database=db, document_models=[CategoryDoc, OrderDoc])

    results = []
    for bm in benchmarks:
        task = progress.add_task(f"{bm.library.value}: {bm.name}", total=None)
        timings = []
        for _ in range(ITERATIONS):
            timer = AsyncTimer()
            async with timer:
                await bm.func(ctx)
            timings.append(timer.result.elapsed_seconds)
        results.append(_compute_stats(bm, timings))
        progress.update(
            task, completed=True, description=f"[green]{bm.library.value}: {bm.name}"
        )
        progress.stop_task(task)

    client.close()
    return results
