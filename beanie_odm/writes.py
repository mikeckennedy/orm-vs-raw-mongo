import uuid
from datetime import datetime

from benchmarks.registry import benchmark, Library, OpType
from models.beanie_models import CategoryDoc, OrderDoc, Address, Payment, LineItem, StatusEntry
from seeding.generator import DataGenerator

_gen = DataGenerator(seed=99)


def _make_category_doc() -> CategoryDoc:
    uid = uuid.uuid4().hex
    raw = _gen.make_one_category(index=0)
    return CategoryDoc(
        name=f"bench-{uid}",
        slug=f"bench-{uid}",
        view_count=raw["view_count"],
        is_active=raw["is_active"],
    )


def _make_order_doc() -> OrderDoc:
    uid = uuid.uuid4().hex
    raw = _gen.make_one_order(index=0)
    return OrderDoc(
        order_number=f"BENCH-{uid}",
        customer_email=raw["customer_email"],
        status=raw["status"],
        total_cents=raw["total_cents"],
        item_count=raw["item_count"],
        created_at=raw["created_at"],
        updated_at=raw["updated_at"],
        shipping_address=Address(**raw["shipping_address"]),
        payment=Payment(**raw["payment"]),
        line_items=[LineItem(**li) for li in raw["line_items"]],
        status_history=[StatusEntry(**sh) for sh in raw["status_history"]],
    )


@benchmark(
    name="insert_single",
    library=Library.BEANIE,
    op_type=OpType.WRITE,
    collection="category",
    description="Insert one Category document",
)
async def insert_single(ctx):
    doc = _make_category_doc()
    await doc.insert()


@benchmark(
    name="insert_batch_100",
    library=Library.BEANIE,
    op_type=OpType.WRITE,
    collection="category",
    description="Insert 100 Category documents in one call",
)
async def insert_batch_100(ctx):
    docs = [_make_category_doc() for _ in range(100)]
    await CategoryDoc.insert_many(docs)


@benchmark(
    name="insert_batch_1000",
    library=Library.BEANIE,
    op_type=OpType.WRITE,
    collection="order",
    description="Insert 1,000 Order documents in one call",
)
async def insert_batch_1000(ctx):
    docs = [_make_order_doc() for _ in range(1000)]
    await OrderDoc.insert_many(docs)


@benchmark(
    name="update_single",
    library=Library.BEANIE,
    op_type=OpType.WRITE,
    collection="order",
    description="Update updated_at on one Order by order_number",
)
async def update_single(ctx):
    order_number = ctx["targets"]["order_number"]
    doc = await OrderDoc.find_one(OrderDoc.order_number == order_number)
    doc.updated_at = datetime.now()
    await doc.save()


@benchmark(
    name="delete_single",
    library=Library.BEANIE,
    op_type=OpType.WRITE,
    collection="category",
    description="Delete one Category by slug",
)
async def delete_single(ctx):
    doc = _make_category_doc()
    await doc.insert()
    await doc.delete()
