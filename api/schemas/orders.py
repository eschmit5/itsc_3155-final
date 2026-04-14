from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from .order_details import OrderDetail

class OrderBase(BaseModel):
    tracking_number: str
    order_status: str = "Pending"
    total_price: Decimal
    customer_id: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    tracking_number: Optional[str] = None
    order_status: Optional[str] = None
    total_price: Optional[Decimal] = None
    customer_id: Optional[int] = None


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    order_details: Optional[list[OrderDetail]] = None

    class ConfigDict:
        from_attributes = True
