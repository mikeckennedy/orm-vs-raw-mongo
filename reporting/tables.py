from collections import defaultdict

from rich.console import Console
from rich.table import Table

from benchmarks.registry import Library, OpType
from benchmarks.runner import BenchmarkResult

console = Console()

LABELS = {
    "read_single_field_category": "Read 1 Field (Category)",
    "read_single_field_order": "Read 1 Field (Order)",
    "read_full_record_category": "Read Full Record (Category)",
    "read_full_record_order": "Read Full Record (Order)",
    "read_100_orders": "Read 100 Orders",
    "read_1000_orders": "Read 1,000 Orders",
    "read_10000_orders": "Read 10,000 Orders",
    "read_100_categories": "Read 100 Categories",
    "read_1000_categories": "Read 1,000 Categories",
    "read_10000_categories": "Read 10,000 Categories",
    "insert_single": "Insert 1",
    "insert_batch_100": "Insert 100",
    "insert_batch_1000": "Insert 1,000",
    "update_single": "Update 1",
    "delete_single": "Delete 1",
}


def _label(name: str) -> str:
    return LABELS.get(name, name.replace("_", " ").title())


def print_results(results: list[BenchmarkResult]):
    if not results:
        console.print("[yellow]No benchmark results to display.")
        return

    # Group results by benchmark name
    by_name: dict[str, dict[str, BenchmarkResult]] = defaultdict(dict)
    for r in results:
        by_name[r.benchmark.name][r.benchmark.library.value] = r

    # Print individual tables
    reads = {k: v for k, v in by_name.items() if any(
        r.benchmark.op_type == OpType.READ for r in v.values()
    )}
    writes = {k: v for k, v in by_name.items() if any(
        r.benchmark.op_type == OpType.WRITE for r in v.values()
    )}

    if reads:
        console.print("\n[bold underline]Read Benchmarks\n")
        _print_comparison_table(reads)

    if writes:
        console.print("\n[bold underline]Write Benchmarks\n")
        _print_comparison_table(writes)

    # Print overhead summary
    if len(by_name) > 0:
        _print_overhead_table(by_name)


def _print_comparison_table(grouped: dict[str, dict[str, BenchmarkResult]]):
    table = Table(show_header=True, header_style="bold magenta", padding=(0, 1))
    table.add_column("Benchmark", style="bold", min_width=30)
    table.add_column("Library", min_width=12)
    table.add_column("Median ms", justify="right")
    table.add_column("Min ms", justify="right")
    table.add_column("Max ms", justify="right")
    table.add_column("P95 ms", justify="right")
    table.add_column("Mean ms", justify="right")

    for name in sorted(grouped.keys()):
        lib_results = grouped[name]
        # Find fastest median
        fastest_median = min(r.median_ms for r in lib_results.values())

        first = True
        for lib_name in ["raw", "dataclasses_raw", "beanie", "mongoengine"]:
            if lib_name not in lib_results:
                continue
            r = lib_results[lib_name]
            is_fastest = r.median_ms == fastest_median
            style = "green" if is_fastest else ""

            table.add_row(
                _label(name) if first else "",
                lib_name,
                f"{r.median_ms:.2f}",
                f"{r.min_ms:.2f}",
                f"{r.max_ms:.2f}",
                f"{r.p95_ms:.2f}",
                f"{r.mean_ms:.2f}",
                style=style,
            )
            first = False

        table.add_section()

    console.print(table)


def _print_overhead_table(grouped: dict[str, dict[str, BenchmarkResult]]):
    console.print("\n[bold underline]Overhead vs Raw PyMongo\n")

    table = Table(show_header=True, header_style="bold magenta", padding=(0, 1))
    table.add_column("Benchmark", style="bold", min_width=30)
    table.add_column("DC + Raw", justify="right")
    table.add_column("Beanie", justify="right")
    table.add_column("MongoEngine", justify="right")

    for name in sorted(grouped.keys()):
        lib_results = grouped[name]
        raw_result = lib_results.get("raw")
        if not raw_result:
            continue

        raw_median = raw_result.median_ms
        dc_r = lib_results.get("dataclasses_raw")
        beanie_r = lib_results.get("beanie")
        me_r = lib_results.get("mongoengine")

        dc_mult = f"{dc_r.median_ms / raw_median:.1f}x" if dc_r and raw_median > 0 else "—"
        beanie_mult = f"{beanie_r.median_ms / raw_median:.1f}x" if beanie_r and raw_median > 0 else "—"
        me_mult = f"{me_r.median_ms / raw_median:.1f}x" if me_r and raw_median > 0 else "—"

        table.add_row(_label(name), dc_mult, beanie_mult, me_mult)

    console.print(table)
