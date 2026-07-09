from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProductStatusEnum(str, Enum):
    active = "active"
    out_of_stock = "out_of_stock"
    hidden = "hidden"

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    category_id: int
    barcode: Optional[str] = None
    name: str = Field(..., max_length=150)
    brand: Optional[str] = None
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    cost_price: Optional[float] = None
    stock_quantity: int = Field(default=0, ge=0)
    minimum_stock: int = Field(default=10, ge=0)
    shelf_location: Optional[str] = None
    image_url: Optional[str] = None
    status: ProductStatusEnum = ProductStatusEnum.active

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    status: Optional[ProductStatusEnum] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LiveAlertSchema(BaseModel):
    priority: str
    icon: str
    text: str
    time: str

class SystemHealthSchema(BaseModel):
    name: str
    status: str
    sync: str
    color: str  # green, yellow, red

class OperationalSummarySchema(BaseModel):
    total_products: int
    categories_count: int
    in_stock_count: int
    out_of_stock_count: int
    active_promotions: int
    registered_customers: int
    orders_today: int
    revenue_today: float

class AdminDashboardOverviewResponse(BaseModel):
    admin_first_name: str
    admin_full_name: str
    active_customers: int
    operational_summary: OperationalSummarySchema
    system_health: List[SystemHealthSchema]
    critical_alerts: List[LiveAlertSchema]