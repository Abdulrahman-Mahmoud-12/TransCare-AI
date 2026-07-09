from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Any
from app.models.user import User, CustomerCategory
from app.models.purchase import Order
from app.models.customer import CustomerAnalytics
from app.schemas.customer import CustomerProfileUpdate

class CustomerService:
    @staticmethod
    def get_analytics(db: Session, customer_id: int) -> dict[str, Any]:
        """
        Retrieves or calculates analytics for a customer dashboard view.
        """
        user = db.query(User).filter(User.id == customer_id).first()
        customer_cat_value = user.customer_category.value if (user and user.customer_category) else "New"

        analytics = db.query(CustomerAnalytics).filter(CustomerAnalytics.customer_id == customer_id).first()
        
        if not analytics:
            total_orders = db.query(Order).filter(Order.customer_id == customer_id).count()
            total_spent = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(Order.customer_id == customer_id).scalar()
            
            return {
                "total_orders": total_orders,
                "total_spent": total_spent,
                "favorite_category": "None yet",
                "favorite_product": "None yet",
                "segment": "New Customer",
                "customer_category": customer_cat_value,
                "return_probability": 0.0,
                "last_purchase": None
            }
            
        return {
            "total_orders": analytics.total_orders,
            "total_spent": analytics.total_spent,
            "favorite_category": analytics.category.name if analytics.category else "N/A",
            "favorite_product": analytics.favorite_product, 
            "segment": analytics.segment or "Standard",
            "customer_category": customer_cat_value,
            "return_probability": float(analytics.return_probability or 0.0) * 100, 
            "last_purchase": analytics.last_purchase
        }

    @staticmethod
    def update_profile_meta(db: Session, user_id: int, data: CustomerProfileUpdate) -> bool:
        """
        Handles updating editable user fields like full name or synchronized profile tags.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
            
        if data.full_name is not None:
            user.full_name = data.full_name
            
        if hasattr(data, 'customer_category') and data.customer_category is not None:
            user.customer_category = data.customer_category
            
        try:
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False