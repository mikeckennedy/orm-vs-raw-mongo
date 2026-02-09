import argparse
import sys

from config import DB_NAME, SEED_COUNT
from db import get_pymongo_client
from benchmarks.registry import Library, OpType


def main():
    parser = argparse.ArgumentParser(
        description="MongoDB ODM vs Raw Performance Benchmark"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # seed command
    seed_parser = subparsers.add_parser("seed", help="Seed the database")
    seed_parser.add_argument(
        "--force", action="store_true", help="Drop and re-seed"
    )

    # reset command
    subparsers.add_parser("reset", help="Drop the benchmark database")

    # run command
    run_parser = subparsers.add_parser("run", help="Run benchmarks")
    run_parser.add_argument(
        "--reads", action="store_true", help="Run only read benchmarks"
    )
    run_parser.add_argument(
        "--writes", action="store_true", help="Run only write benchmarks"
    )
    run_parser.add_argument(
        "--library",
        choices=["raw", "dataclasses_raw", "beanie", "mongoengine"],
        help="Run benchmarks for a specific library only",
    )
    run_parser.add_argument(
        "--no-charts", action="store_true", help="Skip chart generation"
    )

    args = parser.parse_args()

    if args.command == "seed":
        _cmd_seed(args)
    elif args.command == "reset":
        _cmd_reset()
    elif args.command == "run":
        _cmd_run(args)


def _cmd_seed(args):
    from seeding.seeder import seed_database

    client = get_pymongo_client()
    seed_database(client, force=args.force)


def _cmd_reset():
    from seeding.seeder import reset_database

    client = get_pymongo_client()
    reset_database(client)


def _cmd_run(args):
    from seeding.seeder import seed_database
    from benchmarks.runner import run_benchmarks
    from reporting.tables import print_results
    from reporting.charts import generate_charts

    # Auto-seed if needed
    client = get_pymongo_client()
    db = client[DB_NAME]
    cat_count = db.categories.estimated_document_count()
    ord_count = db.orders.estimated_document_count()
    if cat_count < SEED_COUNT or ord_count < SEED_COUNT:
        print("Database not fully seeded. Seeding now...")
        seed_database(client)

    # Determine filters
    library = Library(args.library) if args.library else None

    op_type = None
    if args.reads and not args.writes:
        op_type = OpType.READ
    elif args.writes and not args.reads:
        op_type = OpType.WRITE

    # Run benchmarks
    results = run_benchmarks(library=library, op_type=op_type)

    # Display results
    print_results(results)

    # Generate charts
    if not args.no_charts:
        generate_charts(results)


if __name__ == "__main__":
    main()
