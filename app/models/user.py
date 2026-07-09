from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"

class CustomerCategory(str, enum.Enum):
    NEW = "New"
    REGULAR = "Regular"
    VIP = "VIP"
    CHURN_RISK = "Churn Risk"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    customer_category = Column(Enum(CustomerCategory), nullable=True, default=None)
    admin_id = Column(String(50), unique=True, nullable=True, default=None)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    analytics = relationship("CustomerAnalytics", uselist=False, back_populates="user", cascade="all, delete-orphan")
    shelf_detections = relationship("ShelfDetection", back_populates="uploader")
    inventory_histories = relationship("InventoryHistory", back_populates="modifier")