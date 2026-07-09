from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ChangeType(str, enum.Enum):
    restock = "restock"
    sale = "sale"
    return_type = "return"  # avoiding python keyword conflicts
    damage = "damage"
    manual_update = "manual_update"

class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=True)
    new_stock = Column(Integer, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory_histories")
    modifier = relationship("User", back_populates="inventory_histories")