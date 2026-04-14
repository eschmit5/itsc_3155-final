from datetime import datetime
from sqlalchemy import Column, DATETIME, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), index=True)
    review_text = Column(String(1000))
    score = Column(Integer, nullable=False)
    rating_date = Column(DATETIME, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="ratings")
    menu_item = relationship("MenuItem", back_populates="ratings")