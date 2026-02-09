from benchmarks.registry import Library, OpType, benchmark
from models.mongoengine_models import CategoryDoc, OrderDoc


@benchmark(
    name='read_single_field_category',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='category',
    description="Select only 'name' from one Category by slug (projection)",
)
def read_single_field_category(ctx):
    slug = ctx['targets']['category_slug']
    CategoryDoc.objects(slug=slug).only('name').first()


@benchmark(
    name='read_single_field_order',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='order',
    description="Select only 'customer_email' from one Order by order_number (projection)",
)
def read_single_field_order(ctx):
    order_number = ctx['targets']['order_number']
    OrderDoc.objects(order_number=order_number).only('customer_email').first()


@benchmark(
    name='read_full_record_category',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='category',
    description='Select full Category document by slug',
)
def read_full_record_category(ctx):
    slug = ctx['targets']['category_slug']
    CategoryDoc.objects(slug=slug).first()


@benchmark(
    name='read_full_record_order',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='order',
    description='Select full Order document (with nested subdocs) by order_number',
)
def read_full_record_order(ctx):
    order_number = ctx['targets']['order_number']
    OrderDoc.objects(order_number=order_number).first()


@benchmark(
    name='read_100_orders',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='order',
    description='Select 100 full Order documents by status',
)
def read_100_orders(ctx):
    status = ctx['targets']['bulk_status']
    list(OrderDoc.objects(status=status).limit(100))


@benchmark(
    name='read_1000_orders',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='order',
    description='Select 1,000 full Order documents by status',
)
def read_1000_orders(ctx):
    status = ctx['targets']['bulk_status']
    list(OrderDoc.objects(status=status).limit(1000))


@benchmark(
    name='read_10000_orders',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='order',
    description='Select 10,000 full Order documents by status',
)
def read_10000_orders(ctx):
    status = ctx['targets']['bulk_status']
    list(OrderDoc.objects(status=status).limit(10000))


@benchmark(
    name='read_100_categories',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='category',
    description='Select 100 Categories sorted by view_count descending',
)
def read_100_categories(ctx):
    list(CategoryDoc.objects.order_by('-view_count').limit(100))


@benchmark(
    name='read_1000_categories',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='category',
    description='Select 1,000 Categories sorted by view_count descending',
)
def read_1000_categories(ctx):
    list(CategoryDoc.objects.order_by('-view_count').limit(1000))


@benchmark(
    name='read_10000_categories',
    library=Library.MONGOENGINE,
    op_type=OpType.READ,
    collection='category',
    description='Select 10,000 Categories sorted by view_count descending',
)
def read_10000_categories(ctx):
    list(CategoryDoc.objects.order_by('-view_count').limit(10000))
