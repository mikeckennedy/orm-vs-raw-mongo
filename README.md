# ORM vs Raw MongoDB Benchmarks

> **Read the full article:** [Going Raw Dog on the Database](https://mkennedy.codes/posts/going-raw-dog-on-the-database/) -- After 25+ years of championing ORMs, Michael Kennedy makes the case for abandoning them in favor of raw database queries paired with Python dataclasses. The **Raw+DC pattern** delivers better AI coding assistance, fewer dependencies, and comparable or superior performance -- all while keeping type safety at your data access boundaries. This repo contains the benchmark code behind those findings.

A performance benchmark suite comparing four Python approaches to MongoDB:

| Approach | Driver | Style |
|---|---|---|
| **Raw PyMongo** | pymongo (sync) | Plain dicts |
| **Dataclasses + Raw** | pymongo (sync) | Dicts converted to `@dataclass` objects |
| **Beanie** | motor (async) | Pydantic-based async ODM |
| **MongoEngine** | pymongo (sync) | Traditional sync ODM |

## What It Measures

**Read benchmarks** (per library):
- Single-field projection (category name, order email)
- Full document fetch (simple category, complex order with nested subdocs)
- Bulk reads: 100 / 1,000 / 10,000 orders by status
- Bulk reads: 100 / 1,000 / 10,000 categories sorted by view count

**Write benchmarks** (per library):
- Single insert
- Batch insert (100 categories, 1,000 orders)
- Single update
- Single delete

Each benchmark runs 10 iterations and reports median, min, max, p95, and mean times in milliseconds.

## Requirements

- Python 3.13+
- MongoDB running on `localhost:27017` (no auth)

## Setup

```bash
python -m venv venv
source venv/bin/activate
uv pip install -e .
```

## Usage

### Seed the database

Populates `categories` and `orders` collections with 100K documents each, then creates indexes.

```bash
python main.py seed            # Seed (skips if already populated)
python main.py seed --force    # Drop and re-seed from scratch
```

### Run benchmarks

```bash
python main.py run                         # Run everything
python main.py run --reads                 # Read benchmarks only
python main.py run --writes                # Write benchmarks only
python main.py run --library beanie        # Single library only
python main.py run --library raw --reads   # Combine filters
python main.py run --no-charts             # Skip chart generation
```

The `run` command auto-seeds if the database isn't populated.

### Reset

```bash
python main.py reset    # Drop the entire benchmark database
```

## Output

Results are displayed as Rich tables in the terminal:

- **Comparison table** -- side-by-side timings per benchmark, fastest highlighted in green
- **Overhead table** -- multiplier showing how much slower each ODM is vs raw PyMongo

Charts are saved to `output/`:

- `read_benchmarks.png` -- grouped bar chart of read timings
- `write_benchmarks.png` -- grouped bar chart of write timings
- `overhead_comparison.png` -- overhead multiplier vs raw baseline

## Project Structure

```
main.py                  # CLI entry point
config.py                # Constants (URI, DB name, iterations, seed count)
db.py                    # Connection helpers

models/                  # Data models for each approach
raw/                     # Raw PyMongo benchmarks (dicts)
dataclasses_raw/         # Dataclasses + PyMongo benchmarks
beanie_odm/              # Beanie async ODM benchmarks
mongoengine_odm/         # MongoEngine sync ODM benchmarks

benchmarks/              # Registry, runner, and timing utilities
seeding/                 # Data generation and database seeding
reporting/               # Rich tables and Matplotlib charts
output/                  # Generated chart PNGs
```
