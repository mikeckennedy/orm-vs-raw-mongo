from benchmarks.registry import Library, OpType, benchmark


@benchmark(
    name='read_single_field_category',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='category',
    description="Select only 'name' from one Category by slug (projection)",
)
def read_single_field_category(ctx):
    db = ctx['db']
    slug = ctx['targets']['category_slug']
    db.categories.find_one({'slug': slug}, {'name': 1, '_id': 0})


@benchmark(
    name='read_single_field_order',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='order',
    description="Select only 'customer_email' from one Order by order_number (projection)",
)
def read_single_field_order(ctx):
    db = ctx['db']
    order_number = ctx['targets']['order_number']
    db.orders.find_one({'order_number': order_number}, {'customer_email': 1, '_id': 0})


@benchmark(
    name='read_full_record_category',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='category',
    description='Select full Category document by slug',
)
def read_full_record_category(ctx):
    db = ctx['db']
    slug = ctx['targets']['category_slug']
    db.categories.find_one({'slug': slug})


@benchmark(
    name='read_full_record_order',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='order',
    description='Select full Order document (with nested subdocs) by order_number',
)
def read_full_record_order(ctx):
    db = ctx['db']
    order_number = ctx['targets']['order_number']
    db.orders.find_one({'order_number': order_number})


@benchmark(
    name='read_100_orders',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='order',
    description='Select 100 full Order documents by status',
)
def read_100_orders(ctx):
    db = ctx['db']
    status = ctx['targets']['bulk_status']
    list(db.orders.find({'status': status}).limit(100))


@benchmark(
    name='read_1000_orders',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='order',
    description='Select 1,000 full Order documents by status',
)
def read_1000_orders(ctx):
    db = ctx['db']
    status = ctx['targets']['bulk_status']
    list(db.orders.find({'status': status}).limit(1000))


@benchmark(
    name='read_10000_orders',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='order',
    description='Select 10,000 full Order documents by status',
)
def read_10000_orders(ctx):
    db = ctx['db']
    status = ctx['targets']['bulk_status']
    list(db.orders.find({'status': status}).limit(10000))


@benchmark(
    name='read_100_categories',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='category',
    description='Select 100 Categories sorted by view_count descending',
)
def read_100_categories(ctx):
    db = ctx['db']
    list(db.categories.find().sort('view_count', -1).limit(100))


@benchmark(
    name='read_1000_categories',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='category',
    description='Select 1,000 Categories sorted by view_count descending',
)
def read_1000_categories(ctx):
    db = ctx['db']
    list(db.categories.find().sort('view_count', -1).limit(1000))


@benchmark(
    name='read_10000_categories',
    library=Library.RAW,
    op_type=OpType.READ,
    collection='category',
    description='Select 10,000 Categories sorted by view_count descending',
)
def read_10000_categories(ctx):
    db = ctx['db']
    list(db.categories.find().sort('view_count', -1).limit(10000))
