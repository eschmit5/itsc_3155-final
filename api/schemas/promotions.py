from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PromotionBase(BaseModel):
    promotion_code: str
    expiration_date: Optional[datetime] = None
    order_id: Optional[int] = None
    menu_item_id: Optional[int] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    promotion_code: Optional[str] = None
    expiration_date: Optional[datetime] = None
    order_id: Optional[int] = None
    menu_item_id: Optional[int] = None


class Promotion(PromotionBase):
    id: int

    class ConfigDict:
        from_attributes = True