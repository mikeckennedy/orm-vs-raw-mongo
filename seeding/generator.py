import random
from datetime import datetime, timedelta

from faker import Faker

PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay']
ORDER_STATUSES = [
    'pending',
    'confirmed',
    'processing',
    'shipped',
    'delivered',
    'cancelled',
]


class DataGenerator:
    def __init__(self, seed: int = 42):
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        self._build_pools()

    def _build_pools(self):
        self.streets = [self.fake.street_address() for _ in range(2_000)]
        self.cities = [self.fake.city() for _ in range(500)]
        self.states = [self.fake.state_abbr() for _ in range(50)]
        self.zip_codes = [self.fake.zipcode() for _ in range(1_000)]
        self.first_names = [self.fake.first_name() for _ in range(500)]
        self.last_names = [self.fake.last_name() for _ in range(500)]
        self.email_domains = [
            'gmail.com',
            'yahoo.com',
            'outlook.com',
            'company.co',
            'example.com',
            'fastmail.com',
            'proton.me',
            'icloud.com',
        ]
        self.product_names = [self.fake.catch_phrase() for _ in range(500)]
        self.category_words = [self.fake.word() for _ in range(2_000)]

        # Pre-compute timestamp range: 2023-01-01 to 2025-06-01
        self._ts_start = int(datetime(2023, 1, 1).timestamp())
        self._ts_end = int(datetime(2025, 6, 1).timestamp())

    def _random_email(self) -> str:
        first = random.choice(self.first_names).lower()
        last = random.choice(self.last_names).lower()
        domain = random.choice(self.email_domains)
        return f'{first}.{last}@{domain}'

    def _random_datetime(self) -> datetime:
        ts = random.randint(self._ts_start, self._ts_end)
        return datetime.fromtimestamp(ts)

    def _random_address(self) -> dict:
        return {
            'street': random.choice(self.streets),
            'city': random.choice(self.cities),
            'state': random.choice(self.states),
            'zip_code': random.choice(self.zip_codes),
            'country': 'US',
        }

    def _random_line_items(self, count: int) -> list[dict]:
        items = []
        for _ in range(count):
            items.append(
                {
                    'sku': f'SKU-{random.randint(10000, 99999)}',
                    'name': random.choice(self.product_names),
                    'quantity': random.randint(1, 10),
                    'unit_price_cents': random.randint(299, 49999),
                }
            )
        return items

    def _random_status_history(self, final_status: str, created_at: datetime) -> list[dict]:
        status_order = ORDER_STATUSES[: ORDER_STATUSES.index(final_status) + 1]
        history = []
        t = created_at
        for s in status_order:
            history.append({'status': s, 'changed_at': t})
            t = t + timedelta(hours=random.randint(1, 48))
        return history

    def make_one_category(self, index: int) -> dict:
        word = random.choice(self.category_words)
        return {
            'name': f'{word}-{index}',
            'slug': f'{word}-{index}',
            'view_count': random.randint(0, 500_000),
            'is_active': random.random() < 0.8,
        }

    def make_one_order(self, index: int) -> dict:
        status = random.choice(ORDER_STATUSES)
        created_at = self._random_datetime()
        line_items = self._random_line_items(random.randint(2, 5))
        total = sum(li['unit_price_cents'] * li['quantity'] for li in line_items)

        return {
            'order_number': f'ORD-{index:08d}',
            'customer_email': self._random_email(),
            'status': status,
            'total_cents': total,
            'item_count': len(line_items),
            'created_at': created_at,
            'updated_at': created_at + timedelta(hours=random.randint(0, 72)),
            'shipping_address': self._random_address(),
            'payment': {
                'method': random.choice(PAYMENT_METHODS),
                'last_four': f'{random.randint(1000, 9999)}',
                'charged_cents': total,
            },
            'line_items': line_items,
            'status_history': self._random_status_history(status, created_at),
        }

    def generate_categories_batched(self, count: int, batch_size: int):
        batch = []
        for i in range(count):
            batch.append(self.make_one_category(i))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def generate_orders_batched(self, count: int, batch_size: int):
        batch = []
        for i in range(count):
            batch.append(self.make_one_order(i))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
