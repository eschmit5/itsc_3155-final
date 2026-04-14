from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class MenuItemBase(BaseModel):
    dish: str
    ingredients: Optional[str] = None
    price: Decimal
    calories: Optional[int] = None
    food_category: Optional[str] = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    dish: Optional[str] = None
    ingredients: Optional[str] = None
    price: Optional[Decimal] = None
    calories: Optional[int] = None
    food_category: Optional[str] = None


class MenuItem(MenuItemBase):
    id: int

    class ConfigDict:
        from_attributes = True