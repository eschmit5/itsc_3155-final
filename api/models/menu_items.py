from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dish = Column(String(100), nullable=False)
    ingredients = Column(String(1000))
    price = Column(Numeric(10, 2), nullable=False, default=0.00)
    calories = Column(Integer)
    food_category = Column(String(50))

    order_details = relationship("OrderDetail", back_populates="menu_item")
    ratings = relationship("Rating", back_populates="menu_item")
    promotions = relationship("Promotion", back_populates="menu_item")
    resources = relationship("Resource", back_populates="menu_item")