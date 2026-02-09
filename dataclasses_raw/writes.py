import uuid
from datetime import datetime

from benchmarks.registry import benchmark, Library, OpType
from seeding.generator import DataGenerator

_gen = DataGenerator(seed=99)


def _make_category():
    uid = uuid.uuid4().hex
    doc = _gen.make_one_category(index=0)
    doc["name"] = f"bench-{uid}"
    doc["slug"] = f"bench-{uid}"
    doc["_benchmark"] = True
    return doc


def _make_order():
    uid = uuid.uuid4().hex
    doc = _gen.make_one_order(index=0)
    doc["order_number"] = f"BENCH-{uid}"
    doc["_benchmark"] = True
    return doc


@benchmark(
    name="insert_single",
    library=Library.DATACLASSES_RAW,
    op_type=OpType.WRITE,
    collection="category",
    description="Insert one Category document (raw + dataclass layer)",
)
def insert_single(ctx):
    db = ctx["db"]
    db.categories.insert_one(_make_category())


@benchmark(
    name="insert_batch_100",
    library=Library.DATACLASSES_RAW,
    op_type=OpType.WRITE,
    collection="category",
    description="Insert 100 Category documents in one call (raw + dataclass layer)",
)
def insert_batch_100(ctx):
    db = ctx["db"]
    docs = [_make_category() for _ in range(100)]
    db.categories.insert_many(docs, ordered=False)


@benchmark(
    name="insert_batch_1000",
    library=Library.DATACLASSES_RAW,
    op_type=OpType.WRITE,
    collection="order",
    description="Insert 1,000 Order documents in one call (raw + dataclass layer)",
)
def insert_batch_1000(ctx):
    db = ctx["db"]
    docs = [_make_order() for _ in range(1000)]
    db.orders.insert_many(docs, ordered=False)


@benchmark(
    name="update_single",
    library=Library.DATACLASSES_RAW,
    op_type=OpType.WRITE,
    collection="order",
    description="Update updated_at on one Order by order_number (raw + dataclass layer)",
)
def update_single(ctx):
    db = ctx["db"]
    order_number = ctx["targets"]["order_number"]
    db.orders.update_one(
        {"order_number": order_number},
        {"$set": {"updated_at": datetime.now()}},
    )


@benchmark(
    name="delete_single",
    library=Library.DATACLASSES_RAW,
    op_type=OpType.WRITE,
    collection="category",
    description="Delete one Category by slug (raw + dataclass layer)",
)
def delete_single(ctx):
    db = ctx["db"]
    doc = _make_category()
    db.categories.insert_one(doc)
    db.categories.delete_one({"slug": doc["slug"]})
