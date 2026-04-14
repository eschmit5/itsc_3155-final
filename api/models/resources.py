from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False, server_default="0.00")
    unit = Column(String(20), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), index=True)

    menu_item = relationship("MenuItem", back_populates="resources")