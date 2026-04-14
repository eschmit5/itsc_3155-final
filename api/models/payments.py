from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    card_information = Column(String(200))
    transaction_status = Column(String(20), default="Pending")
    payment_type = Column(String(50))

    order = relationship("Order", back_populates="payment")