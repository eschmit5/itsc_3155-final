from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RatingBase(BaseModel):
    customer_id: Optional[int] = None
    menu_item_id: Optional[int] = None
    review_text: Optional[str] = None
    score: int


class RatingCreate(RatingBase):
    pass


class RatingUpdate(BaseModel):
    customer_id: Optional[int] = None
    menu_item_id: Optional[int] = None
    review_text: Optional[str] = None
    score: Optional[int] = None


class Rating(RatingBase):
    id: int
    rating_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True