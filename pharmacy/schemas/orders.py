from pydantic import BaseModel

from pharmacy.schemas.cart_items import CartItemSchema

class OrderSchema(BaseModel):
    id: int
    cart_items: list[CartItemSchema]