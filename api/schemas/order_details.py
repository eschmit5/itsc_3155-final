from typing import Optional
from pydantic import BaseModel


class OrderDetailBase(BaseModel):
    order_id: int
    menu_item_id: int
    number_of_items: Optional[int] = None
    description: Optional[str] = None


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    menu_item_id: Optional[int] = None
    number_of_items: Optional[int] = None
    description: Optional[str] = None


class OrderDetail(OrderDetailBase):
    id: int

    class ConfigDict:
        from_attributes = True