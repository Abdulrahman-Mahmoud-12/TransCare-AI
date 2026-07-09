from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import Any, Dict, List
import calendar

from app.models import (
    User, 
    Order, 
    OrderItem,
    Product,
    Offer,
    Category,
    CustomerAnalytics,
    CustomerCategory
    )


class DashboardService:
    @staticmethod
    def get_summary_statistics(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Calculates main metric tiles + dynamic MoM trend variance analysis.
        """
        # 1. Total statistics calculation
        stats = db.query(
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(Order.total_price), 0).label("total_spent"),
            func.coalesce(func.sum(Order.total_discount), 0).label("total_saved")
        ).filter(Order.customer_id == customer_id, Order.status == "completed").first()

        total_spending = float(stats.total_spent) if stats else 0.0

        # 2. Dynamic Trend Calculation (Current Month spending vs Last Month spending)
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        last_month_end = current_month_start - timedelta(seconds=1)

        current_month_spent = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
            Order.customer_id == customer_id,
            Order.status == "completed",
            Order.created_at >= current_month_start
        ).scalar() or 0

        last_month_spent = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
            Order.customer_id == customer_id,
            Order.status == "completed",
            Order.created_at >= last_month_start,
            Order.created_at <= last_month_end
        ).scalar() or 0

        trend_value = None
        trend_direction = "up"
        if last_month_spent > 0:
            diff = ((float(current_month_spent) - float(last_month_spent)) / float(last_month_spent)) * 100
            trend_direction = "up" if diff >= 0 else "down"
            trend_value = f"{'+' if diff >= 0 else ''}{round(diff, 1)}%"
        elif current_month_spent > 0:
            trend_value = "+100%"
            trend_direction = "up"

        # 3. Dynamic Favorite Category extraction
        fav_cat_query = db.query(
            Product.category_id, 
            func.count(OrderItem.id).label("item_count")
        ).join(OrderItem, Product.id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .filter(Order.customer_id == customer_id, Order.status == "completed")\
         .group_by(Product.category_id)\
         .order_by(desc("item_count")).first()
        
        fav_category = "None yet"
        if fav_cat_query:
            cat = db.query(Category).filter(Category.id == fav_cat_query.category_id).first()
            if cat:
                fav_category = cat.name

        top_products = (
            db.query(
                Product.id.label("product_id"),
                Product.name.label("name"),
                Product.brand.label("brand"),
                Product.price.label("price"),
                Category.name.label("category_name"),
                func.count(OrderItem.id).label("purchase_count")
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .join(Category, Category.id == Product.category_id)
            .filter(Order.customer_id == customer_id)
            .group_by(Product.id, Category.name)
            .order_by(func.count(OrderItem.id).desc())
            .limit(5)
            .all()
        )

        favorite_products_list = [
            {
                "product_id": p.product_id,
                "name": p.name,
                "brand": p.brand,
                "price": float(p.price),
                "category_name": p.category_name,
                "purchase_count": p.purchase_count,
                "discount_percentage": 0 # Can map to your dynamic deals table if available
            }
            for p in top_products
        ]

        return {
            "total_orders": stats.total_orders if stats else 0,
            "total_spending": total_spending,
            "total_saved": float(stats.total_saved) if stats else 0.0,
            "favorite_category": fav_category,
            "spending_trend_value": trend_value,
            "spending_trend_direction": trend_direction,
            "favorite_products": favorite_products_list
        }

    @staticmethod
    def get_spending_analytics(db: Session, customer_id: int, period: str) -> Dict[str, Any]:
        """
        Generates interval chart timelines mapping spend matrices over time.
        """
        now = datetime.utcnow()
        labels: List[str] = []
        totals: List[float] = []
        purchases: List[int] = []

        if period == "weekly":
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            today_idx = now.weekday()
            labels = labels[today_idx + 1:] + labels[:today_idx + 1]
            totals = [0.0] * 7
            purchases = [0] * 7
            
            start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            orders = db.query(Order).filter(
                Order.customer_id == customer_id,
                Order.status == "completed",
                Order.created_at >= start_date
            ).all()

            for order in orders:
                days_ago = (now.date() - order.created_at.date()).days
                if 0 <= days_ago < 7:
                    idx = 6 - days_ago
                    totals[idx] += float(order.total_price)
                    purchases[idx] += 1

        elif period == "monthly":
            labels = ["Wk 1", "Wk 2", "Wk 3", "Wk 4"]
            totals = [0.0] * 4
            purchases = [0] * 4
            
            start_date = now - timedelta(days=28)
            orders = db.query(Order).filter(
                Order.customer_id == customer_id,
                Order.status == "completed",
                Order.created_at >= start_date
            ).all()

            for order in orders:
                days_ago = (now - order.created_at).days
                if 0 <= days_ago < 28:
                    idx = 3 - (days_ago // 7)
                    totals[idx] += float(order.total_price)
                    purchases[idx] += 1

        elif period == "yearly":
            month_names = list(calendar.month_abbr)[1:]
            current_month = now.month
            labels = month_names[current_month:] + month_names[:current_month]
            totals = [0.0] * 12
            purchases = [0] * 12
            
            start_date = (now - timedelta(days=365)).replace(day=1)
            orders = db.query(Order).filter(
                Order.customer_id == customer_id,
                Order.status == "completed",
                Order.created_at >= start_date
            ).all()

            for order in orders:
                months_ago = (now.year - order.created_at.year) * 12 + (now.month - order.created_at.month)
                if 0 <= months_ago < 12:
                    idx = 11 - months_ago
                    totals[idx] += float(order.total_price)
                    purchases[idx] += 1

        return {"labels": labels, "totals": totals, "purchases": purchases}

    @staticmethod
    def get_category_distribution(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Aggregates items bought per category.
        """
        results = db.query(
            Category.name,
            func.count(OrderItem.id).label("count")
        ).join(Product, Category.id == Product.category_id)\
         .join(OrderItem, Product.id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .filter(Order.customer_id == customer_id, Order.status == "completed")\
         .group_by(Category.name).all()

        labels = [r[0] for r in results]
        values = [int(r[1]) for r in results]

        if not labels:
            labels = ["No Data"]
            values = [0]

        return {"labels": labels, "values": values}

    @staticmethod
    def get_favorite_products(db: Session, customer_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves top 2 favorite items based on maximum volume purchased by this individual.
        """
        top_items = db.query(
            Product,
            func.count(OrderItem.id).label("purchase_count")
        ).join(OrderItem, Product.id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .filter(Order.customer_id == customer_id, Order.status == "completed")\
         .group_by(Product.id)\
         .order_by(desc("purchase_count"))\
         .limit(2).all()

        output = []
        for product, count in top_items:
            output.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand or "RetailIQ Edge",
                "price": float(product.price),
                "image_url": product.image_url or "/static/images/placeholder-product.png",
                "purchase_count": int(count)
            })
        return output

    @staticmethod
    def get_main_page_recommendations(db: Session) -> List[Dict[str, Any]]:
        """
        Returns recommendations based on active promotional deals (matches main page logic).
        """
        now = datetime.utcnow()
        active_offers = db.query(Offer, Product).join(
            Product, Offer.product_id == Product.id
        ).filter(
            Offer.is_active == True,
            Offer.start_date <= now,
            Offer.end_date >= now
        ).limit(6).all()

        recommendations = []
        for offer, product in active_offers:
            recommendations.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand or "Promoted Deal",
                "price": float(product.price),
                "discount_percentage": float(offer.discount_percentage) if offer.discount_percentage else 0.0,
                "image_url": product.image_url or "/static/images/placeholder-product.png",
                "tag": f"-{int(offer.discount_percentage)}% OFF" if offer.discount_percentage else "Active Deal"
            })
        return recommendations

    @staticmethod
    def get_shopping_insights_and_patterns(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Generates dynamic personalized customer data insights and structural habits.
        """
        orders = db.query(Order).filter(Order.customer_id == customer_id, Order.status == "completed").all()
        
        # Default responses for sparse database contexts
        avg_basket = 0.0
        peak_hour_str = "No history yet"
        velocity_insight = "Keep shopping to unlock dynamic insights."
        
        if orders:
            avg_basket = float(sum(o.total_price for o in orders) / len(orders))
            
            # Find peak hour pattern from orders
            hours = [o.created_at.hour for o in orders if o.created_at]
            if hours:
                peak_hour = max(set(hours), key=hours.count)
                period_str = "PM" if peak_hour >= 12 else "AM"
                display_hour = peak_hour % 12
                display_hour = 12 if display_hour == 0 else display_hour
                peak_hour_str = f"{display_hour}:00 {period_str}"

            if len(orders) >= 3:
                velocity_insight = f"Your average cart evaluation stands clear at {round(avg_basket, 2)} EGP across your checkout lifecycle."
            else:
                velocity_insight = "Your insight track will expand as more orders are completed."

        return {
            "insights": [
                {"title": "Average Order Basket", "desc": f"Your structural ticket size averages {round(avg_basket, 2)} EGP per trip.", "icon": "💡"},
                {"title": "Velocity Track", "desc": velocity_insight, "icon": "📊"}
            ],
            "patterns": {
                "peak_time": peak_hour_str,
                "frequency": "Regular Visitor" if len(orders) > 5 else "New Explorer"
            }
        }

    @staticmethod
    def get_rewards_tier_progress(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Computes progress toward the next loyalty tier based on overall purchase values.
        """
        user = db.query(User).filter(User.id == customer_id).first()
        current_tier = user.customer_category.value if (user and user.customer_category) else "New"

        total_spent = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
            Order.customer_id == customer_id, Order.status == "completed"
        ).scalar() or 0
        total_spent = float(total_spent)

        # Establish clear spending tiers milestones
        tier_milestones = {"New": 1000.0, "Regular": 5000.0, "VIP": 15000.0, "Churn Risk": 5000.0}
        target_cap = tier_milestones.get(current_tier, 5000.0)
        
        progress_percentage = min(int((total_spent / target_cap) * 100), 100)
        points_accumulated = int(total_spent // 10) # 1 Point per 10 EGP

        return {
            "current_tier": current_tier,
            "points": points_accumulated,
            "progress_percentage": progress_percentage,
            "next_tier_milestone": f"{int(total_spent)} / {int(target_cap)} EGP to next checkpoint"
        }