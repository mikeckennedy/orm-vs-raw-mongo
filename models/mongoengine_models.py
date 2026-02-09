import mongoengine as me


# --- Embedded documents ---

class Address(me.EmbeddedDocument):
    street = me.StringField(required=True)
    city = me.StringField(required=True)
    state = me.StringField(required=True)
    zip_code = me.StringField(required=True)
    country = me.StringField(required=True)


class Payment(me.EmbeddedDocument):
    method = me.StringField(required=True)
    last_four = me.StringField(required=True)
    charged_cents = me.IntField(required=True)


class LineItem(me.EmbeddedDocument):
    sku = me.StringField(required=True)
    name = me.StringField(required=True)
    quantity = me.IntField(required=True)
    unit_price_cents = me.IntField(required=True)


class StatusEntry(me.EmbeddedDocument):
    status = me.StringField(required=True)
    changed_at = me.DateTimeField(required=True)


# --- Top-level documents ---

class CategoryDoc(me.Document):
    name = me.StringField(required=True, unique=True)
    slug = me.StringField(required=True, unique=True)
    view_count = me.IntField(required=True)
    is_active = me.BooleanField(required=True)

    meta = {
        "collection": "categories",
        "indexes": [
            "name",
            "slug",
            {"fields": ["-view_count"]},
        ],
    }


class OrderDoc(me.Document):
    order_number = me.StringField(required=True, unique=True)
    customer_email = me.StringField(required=True)
    status = me.StringField(required=True)
    total_cents = me.IntField(required=True)
    item_count = me.IntField(required=True)
    created_at = me.DateTimeField(required=True)
    updated_at = me.DateTimeField(required=True)
    shipping_address = me.EmbeddedDocumentField(Address, required=True)
    payment = me.EmbeddedDocumentField(Payment, required=True)
    line_items = me.EmbeddedDocumentListField(LineItem, required=True)
    status_history = me.EmbeddedDocumentListField(StatusEntry, required=True)

    meta = {
        "collection": "orders",
        "indexes": [
            "order_number",
            "customer_email",
            "status",
            {"fields": ["-total_cents"]},
            {"fields": ["-created_at"]},
        ],
    }
