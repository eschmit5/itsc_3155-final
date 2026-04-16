from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from .order_details import OrderDetail

class OrderBase(BaseModel):
    tracking_number: str = Field(..., min_length=1, max_length=50, description="Unique tracking number for your order")
    order_status: str = Field(default="Pending", description="Current status of your order")
    total_price: Decimal = Field(..., ge=0, description="Total price of your order")
    customer_id: int = Field(..., gt=0, description="ID of the customer who placed the order")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    tracking_number: Optional[str] = Field(None, min_length=1, max_length=50)
    order_status: Optional[str] = None
    total_price: Optional[Decimal] = Field(None, ge=0)
    customer_id: Optional[int] = Field(None, gt=0)

class Order(OrderBase):
    id: int = Field(..., description="Unique identifier for the order")
    order_date: Optional[datetime] = Field(None, description="Date and time when the order was placed")
    order_details: Optional[list[OrderDetail]] = Field(default=[], description="List of details for each item in the order")

    class ConfigDict:
        from_attributes = True
