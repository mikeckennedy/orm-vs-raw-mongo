import os
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

from benchmarks.registry import OpType
from benchmarks.runner import BenchmarkResult

COLORS = {
    "raw": "#2196F3",
    "dataclasses_raw": "#9C27B0",
    "beanie": "#FF9800",
    "mongoengine": "#4CAF50",
}

LABELS = {
    "read_single_field_category": "Read 1 Field\n(Category)",
    "read_single_field_order": "Read 1 Field\n(Order)",
    "read_full_record_category": "Read Full Record\n(Category)",
    "read_full_record_order": "Read Full Record\n(Order)",
    "read_100_orders": "Read 100\nOrders",
    "read_1000_orders": "Read 1,000\nOrders",
    "read_10000_orders": "Read 10,000\nOrders",
    "read_100_categories": "Read 100\nCategories",
    "read_1000_categories": "Read 1,000\nCategories",
    "read_10000_categories": "Read 10,000\nCategories",
    "insert_single": "Insert 1",
    "insert_batch_100": "Insert\n100",
    "insert_batch_1000": "Insert\n1,000",
    "update_single": "Update 1",
    "delete_single": "Delete 1",
}


def _label(name: str) -> str:
    return LABELS.get(name, name.replace("_", " ").title())


def generate_charts(results: list[BenchmarkResult], output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)

    by_name: dict[str, dict[str, BenchmarkResult]] = defaultdict(dict)
    for r in results:
        by_name[r.benchmark.name][r.benchmark.library.value] = r

    reads = {
        k: v
        for k, v in by_name.items()
        if any(r.benchmark.op_type == OpType.READ for r in v.values())
    }
    writes = {
        k: v
        for k, v in by_name.items()
        if any(r.benchmark.op_type == OpType.WRITE for r in v.values())
    }

    if reads:
        _bar_chart(reads, "Read Benchmark Results", f"{output_dir}/read_benchmarks.png")
    if writes:
        _bar_chart(
            writes, "Write Benchmark Results", f"{output_dir}/write_benchmarks.png"
        )
    if by_name:
        _overhead_chart(by_name, f"{output_dir}/overhead_comparison.png")


def _bar_chart(
    grouped: dict[str, dict[str, BenchmarkResult]],
    title: str,
    filepath: str,
):
    names = sorted(grouped.keys())
    libraries = ["raw", "dataclasses_raw", "beanie", "mongoengine"]
    n = len(names)
    bar_width = 0.2

    fig, ax = plt.subplots(figsize=(max(12, n * 1.5), 6))

    for i, lib in enumerate(libraries):
        values = []
        for name in names:
            r = grouped[name].get(lib)
            values.append(r.median_ms if r else 0)

        positions = [x + i * bar_width for x in range(n)]
        display = lib.replace("_", " ").title()
        ax.bar(positions, values, bar_width, label=display, color=COLORS[lib])

    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Median Time (ms)")
    ax.set_title(title)
    ax.set_xticks([x + bar_width * 1.5 for x in range(n)])
    ax.set_xticklabels([_label(n) for n in names], rotation=45, ha="right", fontsize=8)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)
    print(f"Chart saved: {filepath}")


def _overhead_chart(
    grouped: dict[str, dict[str, BenchmarkResult]],
    filepath: str,
):
    names = sorted(grouped.keys())
    dc_overheads = []
    beanie_overheads = []
    me_overheads = []

    for name in names:
        lib_results = grouped[name]
        raw_r = lib_results.get("raw")
        if not raw_r or raw_r.median_ms == 0:
            dc_overheads.append(0)
            beanie_overheads.append(0)
            me_overheads.append(0)
            continue

        dc_r = lib_results.get("dataclasses_raw")
        beanie_r = lib_results.get("beanie")
        me_r = lib_results.get("mongoengine")
        dc_overheads.append(dc_r.median_ms / raw_r.median_ms if dc_r else 0)
        beanie_overheads.append(beanie_r.median_ms / raw_r.median_ms if beanie_r else 0)
        me_overheads.append(me_r.median_ms / raw_r.median_ms if me_r else 0)

    n = len(names)
    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(max(12, n * 1.5), 6))

    positions_d = [x for x in range(n)]
    positions_b = [x + bar_width for x in range(n)]
    positions_m = [x + bar_width * 2 for x in range(n)]

    ax.bar(
        positions_d,
        dc_overheads,
        bar_width,
        label="Dataclasses + Raw",
        color=COLORS["dataclasses_raw"],
    )
    ax.bar(
        positions_b, beanie_overheads, bar_width, label="Beanie", color=COLORS["beanie"]
    )
    ax.bar(
        positions_m,
        me_overheads,
        bar_width,
        label="MongoEngine",
        color=COLORS["mongoengine"],
    )

    ax.axhline(
        y=1.0,
        color=COLORS["raw"],
        linestyle="--",
        linewidth=2,
        label="Raw baseline (1.0x)",
    )

    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Overhead Multiplier (vs Raw)")
    ax.set_title("ODM Overhead Compared to Raw PyMongo")
    ax.set_xticks([x + bar_width for x in range(n)])
    ax.set_xticklabels([_label(n) for n in names], rotation=45, ha="right", fontsize=8)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)
    print(f"Chart saved: {filepath}")
