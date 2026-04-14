from sqlalchemy import Column, DATETIME, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    promotion_code = Column(String(50), nullable=False, unique=True, index=True)
    expiration_date = Column(DATETIME)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True, index=True)

    # TODO: Consider if we should add more details about the promotion, such as discount amount or %.
    # Could enable automatic application of promotions, but would require much more logic to determine when and where to apply the discount.

    order = relationship("Order", back_populates="promotions")
    menu_item = relationship("MenuItem", back_populates="promotions")