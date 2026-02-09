from beanie import Document
from pydantic import BaseModel
from pymongo import IndexModel
from datetime import datetime


# --- Subdocument models (plain Pydantic) ---


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class Payment(BaseModel):
    method: str
    last_four: str
    charged_cents: int


class LineItem(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_price_cents: int


class StatusEntry(BaseModel):
    status: str
    changed_at: datetime


# --- Projection models ---


class CategoryNameProjection(BaseModel):
    name: str


class OrderEmailProjection(BaseModel):
    customer_email: str


# --- Document models ---


class CategoryDoc(Document):
    name: str
    slug: str
    view_count: int
    is_active: bool

    class Settings:
        name = "categories"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("slug", 1)], unique=True),
            IndexModel([("view_count", -1)]),
        ]


class OrderDoc(Document):
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

    class Settings:
        name = "orders"
        indexes = [
            IndexModel([("order_number", 1)], unique=True),
            IndexModel([("customer_email", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("total_cents", -1)]),
            IndexModel([("created_at", -1)]),
        ]
