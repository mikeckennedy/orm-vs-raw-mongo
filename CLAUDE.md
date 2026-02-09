# CLAUDE.md

## Project Overview

Benchmark suite comparing MongoDB access patterns in Python: raw PyMongo, dataclasses + PyMongo, Beanie (async ODM), and MongoEngine (sync ODM). Measures read/write performance across single-document, batch, and bulk operations on 100K-record collections.

## Tech Stack

- **Python 3.14** with `venv` (not `.venv`)
- **Package manager**: `uv pip` (never bare `pip`)
- **MongoDB 8.x** on `localhost:27017`, no authentication
- **Database**: `orm_benchmark`
- **Key dependencies**: pymongo, motor, beanie, mongoengine, faker, rich, matplotlib

## Project Structure

```
main.py              # CLI entry point (seed | reset | run)
config.py            # Constants: MONGO_URI, DB_NAME, ITERATIONS, SEED_COUNT, BATCH_SIZE
db.py                # Connection helpers: PyMongo, Motor, MongoEngine

models/
  beanie_models.py       # Beanie Document models (Pydantic-based, async)
  dataclass_models.py    # stdlib dataclasses + from_doc() converters
  mongoengine_models.py  # MongoEngine Document models

raw/                 # Benchmarks using raw PyMongo dicts
dataclasses_raw/     # Benchmarks using PyMongo + dataclass conversion
beanie_odm/          # Benchmarks using Beanie (async)
mongoengine_odm/     # Benchmarks using MongoEngine (sync)

benchmarks/
  registry.py        # @benchmark decorator, Library/OpType enums, global registry
  runner.py          # Executes benchmarks, computes stats (median, min, max, p95, mean)
  timer.py           # sync_timer context manager + AsyncTimer

seeding/
  generator.py       # Faker-based DataGenerator for categories and orders
  seeder.py          # Bulk-inserts 100K docs per collection, creates indexes

reporting/
  tables.py          # Rich tables: comparison + overhead summary
  charts.py          # Matplotlib bar charts: reads, writes, overhead multiplier

output/              # Generated PNG charts
```

## CLI Usage

```bash
python main.py seed [--force]        # Seed database (--force drops and re-seeds)
python main.py reset                 # Drop the benchmark database
python main.py run                   # Run all benchmarks
python main.py run --reads           # Read benchmarks only
python main.py run --writes          # Write benchmarks only
python main.py run --library raw     # Single library (raw | dataclasses_raw | beanie | mongoengine)
python main.py run --no-charts       # Skip chart generation
```

## Architecture Notes

- Benchmarks self-register via the `@benchmark` decorator in `benchmarks/registry.py`
- Each library module (`raw/`, `beanie_odm/`, etc.) has `reads.py` and `writes.py`
- The runner imports all modules to trigger registration, then filters by library/op_type
- Sync benchmarks (raw, dataclasses_raw, mongoengine) run first, then async (beanie)
- Write benchmarks tag docs with `_benchmark: True` for cleanup after each batch
- `preselect_targets()` picks random query targets shared across all libraries for fair comparison

## Known Gotcha

When indexes already exist in MongoDB (created via PyMongo seeder), Beanie's `init_beanie` will fail with `IndexKeySpecsConflict` if index declarations don't match exactly. The Beanie models use `pymongo.IndexModel` with matching `unique=True` flags to avoid this.
