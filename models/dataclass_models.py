from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str


@dataclass(slots=True)
class Payment:
    method: str
    last_four: str
    charged_cents: int


@dataclass(slots=True)
class LineItem:
    sku: str
    name: str
    quantity: int
    unit_price_cents: int


@dataclass(slots=True)
class StatusEntry:
    status: str
    changed_at: datetime


@dataclass(slots=True)
class Category:
    name: str
    slug: str
    view_count: int
    is_active: bool


@dataclass(slots=True)
class Order:
    order_number: str
    customer_email: str
    status: str
    total_cents: int
    item_count: int
    created_at: datetime
    updated_at: datetime
    shipping_address: Address
    payment: Payment
    line_items: list[LineItem]
    status_history: list[StatusEntry]


def category_from_doc(doc: dict) -> Category:
    return Category(
        name=doc["name"],
        slug=doc["slug"],
        view_count=doc["view_count"],
        is_active=doc["is_active"],
    )


def order_from_doc(doc: dict) -> Order:
    return Order(
        order_number=doc["order_number"],
        customer_email=doc["customer_email"],
        status=doc["status"],
        total_cents=doc["total_cents"],
        item_count=doc["item_count"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        shipping_address=Address(**doc["shipping_address"]),
        payment=Payment(**doc["payment"]),
        line_items=[LineItem(**li) for li in doc["line_items"]],
        status_history=[StatusEntry(**sh) for sh in doc["status_history"]],
    )
