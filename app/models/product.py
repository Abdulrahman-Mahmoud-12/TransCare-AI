from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ProductStatus(str, enum.Enum):
    active = "active"
    out_of_stock = "out_of_stock"
    hidden = "hidden"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    barcode = Column(String(50), unique=True, nullable=True)
    name = Column(String(150), nullable=False, index=True)
    brand = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    minimum_stock = Column(Integer, default=10)
    shelf_location = Column(String(50), nullable=True)
    image_url = Column(String(255), nullable=True)
    status = Column(Enum(ProductStatus), default=ProductStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="products")
    offers = relationship("Offer", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    inventory_histories = relationship("InventoryHistory", back_populates="product", cascade="all, delete-orphan")
    favorite_of_analytics = relationship("CustomerAnalytics", back_populates="favorite_prod_rel")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="offers")