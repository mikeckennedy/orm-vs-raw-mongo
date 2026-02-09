from pymongo import MongoClient, DESCENDING
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)

from config import DB_NAME, SEED_COUNT, BATCH_SIZE
from seeding.generator import DataGenerator


def seed_database(client: MongoClient, force: bool = False):
    db = client[DB_NAME]
    gen = DataGenerator(seed=42)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:
        # Seed categories
        cat_count = db.categories.estimated_document_count()
        if not force and cat_count >= SEED_COUNT:
            progress.console.print(
                f"[green]Categories already seeded ({cat_count:,} docs), skipping."
            )
        else:
            if force:
                db.categories.drop()
            task = progress.add_task("Seeding categories...", total=SEED_COUNT)
            for batch in gen.generate_categories_batched(SEED_COUNT, BATCH_SIZE):
                db.categories.insert_many(batch, ordered=False)
                progress.advance(task, len(batch))

        # Seed orders
        ord_count = db.orders.estimated_document_count()
        if not force and ord_count >= SEED_COUNT:
            progress.console.print(
                f"[green]Orders already seeded ({ord_count:,} docs), skipping."
            )
        else:
            if force:
                db.orders.drop()
            task = progress.add_task("Seeding orders...", total=SEED_COUNT)
            for batch in gen.generate_orders_batched(SEED_COUNT, BATCH_SIZE):
                db.orders.insert_many(batch, ordered=False)
                progress.advance(task, len(batch))

    # Create indexes after bulk insert
    _create_indexes(db)


def reset_database(client: MongoClient):
    client.drop_database(DB_NAME)
    print(f"Database '{DB_NAME}' dropped.")


def _create_indexes(db):
    print("Creating indexes...")

    # Category indexes
    db.categories.create_index("name", unique=True)
    db.categories.create_index("slug", unique=True)
    db.categories.create_index([("view_count", DESCENDING)])

    # Order indexes
    db.orders.create_index("order_number", unique=True)
    db.orders.create_index("customer_email")
    db.orders.create_index("status")
    db.orders.create_index([("total_cents", DESCENDING)])
    db.orders.create_index([("created_at", DESCENDING)])

    print("Indexes created.")
