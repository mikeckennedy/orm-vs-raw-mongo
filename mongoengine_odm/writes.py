import uuid
from datetime import datetime

from benchmarks.registry import Library, OpType, benchmark
from models.mongoengine_models import (
    Address,
    CategoryDoc,
    LineItem,
    OrderDoc,
    Payment,
    StatusEntry,
)
from seeding.generator import DataGenerator

_gen = DataGenerator(seed=99)


def _make_category_doc() -> CategoryDoc:
    uid = uuid.uuid4().hex
    raw = _gen.make_one_category(index=0)
    return CategoryDoc(
        name=f'bench-{uid}',
        slug=f'bench-{uid}',
        view_count=raw['view_count'],
        is_active=raw['is_active'],
    )


def _make_order_doc() -> OrderDoc:
    uid = uuid.uuid4().hex
    raw = _gen.make_one_order(index=0)
    return OrderDoc(
        order_number=f'BENCH-{uid}',
        customer_email=raw['customer_email'],
        status=raw['status'],
        total_cents=raw['total_cents'],
        item_count=raw['item_count'],
        created_at=raw['created_at'],
        updated_at=raw['updated_at'],
        shipping_address=Address(**raw['shipping_address']),
        payment=Payment(**raw['payment']),
        line_items=[LineItem(**li) for li in raw['line_items']],
        status_history=[StatusEntry(**sh) for sh in raw['status_history']],
    )


@benchmark(
    name='insert_single',
    library=Library.MONGOENGINE,
    op_type=OpType.WRITE,
    collection='category',
    description='Insert one Category document',
)
def insert_single(ctx):
    doc = _make_category_doc()
    doc.save()


@benchmark(
    name='insert_batch_100',
    library=Library.MONGOENGINE,
    op_type=OpType.WRITE,
    collection='category',
    description='Insert 100 Category documents in one call',
)
def insert_batch_100(ctx):
    docs = [_make_category_doc() for _ in range(100)]
    CategoryDoc.objects.insert(docs)


@benchmark(
    name='insert_batch_1000',
    library=Library.MONGOENGINE,
    op_type=OpType.WRITE,
    collection='order',
    description='Insert 1,000 Order documents in one call',
)
def insert_batch_1000(ctx):
    docs = [_make_order_doc() for _ in range(1000)]
    OrderDoc.objects.insert(docs)


@benchmark(
    name='update_single',
    library=Library.MONGOENGINE,
    op_type=OpType.WRITE,
    collection='order',
    description='Update updated_at on one Order by order_number',
)
def update_single(ctx):
    order_number = ctx['targets']['order_number']
    doc = OrderDoc.objects(order_number=order_number).first()
    doc.updated_at = datetime.now()
    doc.save()


@benchmark(
    name='delete_single',
    library=Library.MONGOENGINE,
    op_type=OpType.WRITE,
    collection='category',
    description='Delete one Category by slug',
)
def delete_single(ctx):
    doc = _make_category_doc()
    doc.save()
    doc.delete()
