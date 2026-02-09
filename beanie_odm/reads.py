from beanie import SortDirection

from benchmarks.registry import Library, OpType, benchmark
from models.beanie_models import (
    CategoryDoc,
    CategoryNameProjection,
    OrderDoc,
    OrderEmailProjection,
)


@benchmark(
    name='read_single_field_category',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='category',
    description="Select only 'name' from one Category by slug (projection)",
)
async def read_single_field_category(ctx):
    slug = ctx['targets']['category_slug']
    await CategoryDoc.find_one(
        CategoryDoc.slug == slug,
        projection_model=CategoryNameProjection,
    )


@benchmark(
    name='read_single_field_order',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='order',
    description="Select only 'customer_email' from one Order by order_number (projection)",
)
async def read_single_field_order(ctx):
    order_number = ctx['targets']['order_number']
    await OrderDoc.find_one(
        OrderDoc.order_number == order_number,
        projection_model=OrderEmailProjection,
    )


@benchmark(
    name='read_full_record_category',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='category',
    description='Select full Category document by slug',
)
async def read_full_record_category(ctx):
    slug = ctx['targets']['category_slug']
    await CategoryDoc.find_one(CategoryDoc.slug == slug)


@benchmark(
    name='read_full_record_order',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='order',
    description='Select full Order document (with nested subdocs) by order_number',
)
async def read_full_record_order(ctx):
    order_number = ctx['targets']['order_number']
    await OrderDoc.find_one(OrderDoc.order_number == order_number)


@benchmark(
    name='read_100_orders',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='order',
    description='Select 100 full Order documents by status',
)
async def read_100_orders(ctx):
    status = ctx['targets']['bulk_status']
    await OrderDoc.find(OrderDoc.status == status).limit(100).to_list()


@benchmark(
    name='read_1000_orders',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='order',
    description='Select 1,000 full Order documents by status',
)
async def read_1000_orders(ctx):
    status = ctx['targets']['bulk_status']
    await OrderDoc.find(OrderDoc.status == status).limit(1000).to_list()


@benchmark(
    name='read_10000_orders',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='order',
    description='Select 10,000 full Order documents by status',
)
async def read_10000_orders(ctx):
    status = ctx['targets']['bulk_status']
    await OrderDoc.find(OrderDoc.status == status).limit(10000).to_list()


@benchmark(
    name='read_100_categories',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='category',
    description='Select 100 Categories sorted by view_count descending',
)
async def read_100_categories(ctx):
    await CategoryDoc.find().sort((CategoryDoc.view_count, SortDirection.DESCENDING)).limit(100).to_list()


@benchmark(
    name='read_1000_categories',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='category',
    description='Select 1,000 Categories sorted by view_count descending',
)
async def read_1000_categories(ctx):
    await CategoryDoc.find().sort((CategoryDoc.view_count, SortDirection.DESCENDING)).limit(1000).to_list()


@benchmark(
    name='read_10000_categories',
    library=Library.BEANIE,
    op_type=OpType.READ,
    collection='category',
    description='Select 10,000 Categories sorted by view_count descending',
)
async def read_10000_categories(ctx):
    await CategoryDoc.find().sort((CategoryDoc.view_count, SortDirection.DESCENDING)).limit(10000).to_list()
