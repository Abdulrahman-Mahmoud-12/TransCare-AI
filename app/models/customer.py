from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"

    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0)
    favorite_category = Column(Integer, ForeignKey("categories.id"), nullable=True)
    favorite_product = Column(Integer, ForeignKey("products.id"), nullable=True)
    segment = Column(String(50), nullable=True)
    return_probability = Column(Numeric(5, 2), nullable=True)
    last_purchase = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analytics")
    favorite_cat_rel = relationship("Category", back_populates="favorite_of_analytics")
    favorite_prod_rel = relationship("Product", back_populates="favorite_of_analytics")