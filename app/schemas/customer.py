from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.user import CustomerCategory

class CustomerAnalyticsBase(BaseModel):
    total_orders: int = 0
    total_spent: Decimal = Decimal("0.0")
    favorite_category: Optional[int] = None
    favorite_product: Optional[int] = None
    segment: Optional[str] = None
    return_probability: Optional[float] = None
    last_purchase: Optional[datetime] = None

class CustomerAnalyticsResponse(CustomerAnalyticsBase):
    customer_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    customer_category: Optional[CustomerCategory] = None
    email: Optional[str] = None