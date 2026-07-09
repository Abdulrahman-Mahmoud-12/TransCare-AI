from app.database import Base
from app.models.user import User, UserRole, CustomerCategory
from app.models.category import Category
from app.models.product import Product, Offer, ProductStatus
from app.models.customer import CustomerAnalytics
from app.models.purchase import Order, OrderItem, PaymentMethod, OrderStatus
from app.models.shelf import ShelfDetection
from app.models.inventory import InventoryHistory
from app.models.report import Report

# Exporting them explicitly makes clean imports possible elsewhere
__all__ = [
    "Base",
    "User",
    "UserRole",
    "CustomerCategory",
    "Category",
    "Product",
    "Offer",
    "ProductStatus",
    "CustomerAnalytics",
    "Order",
    "OrderItem",
    "PaymentMethod",    
    "OrderStatus",
    "ShelfDetection",
    "InventoryHistory",
    "Report",
]