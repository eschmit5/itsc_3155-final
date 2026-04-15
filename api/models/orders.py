from datetime import datetime
from sqlalchemy import Column, DATETIME, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_date = Column(DATETIME, nullable=False, default=datetime.utcnow)
    tracking_number = Column(String(50), unique=True, nullable=False)
    order_status = Column(String(20), default="Pending")
    total_price = Column(Numeric(10, 2), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # TODO: Consider what should go into OrderDetail vs Order.

    customer = relationship("Customer", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)
    promotions = relationship("Promotion", back_populates="order")