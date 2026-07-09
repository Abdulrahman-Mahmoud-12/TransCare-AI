import sys
import os
import random
from decimal import Decimal
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal
# Import BOTH models directly from your app's core definitions instead of the seed folder
from app.models.product import Product
from app.models.category import Category

def seed_products():
    print("📦 Seeding inventory items matching updated category definitions...")
    db: Session = SessionLocal()
    try:
        # Fetch the existing categories that you already ran and saved in your DB
        categories = db.query(Category).all()
        if not categories:
            print("❌ No categories found in the database. Please make sure the categories table has rows!")
            return
        
        products_setup = [
            # --- Drinks ---
            {"name": "Arabica Instant Coffee Jar 200g", "price": 165.00, "cost": 105.00, "cat": "Drinks", "img": "☕"},
            {"name": "Lemon Black Tea 20 Bags", "price": 48.00, "cost": 30.00, "cat": "Drinks", "img": "🍋"},
            {"name": "Mango Nectar Juice 1L", "price": 52.00, "cost": 33.00, "cat": "Drinks", "img": "🥭"},
            {"name": "Sparkling Lemonade 1.25L", "price": 32.00, "cost": 19.00, "cat": "Drinks", "img": "🍋"},
            {"name": "Hazelnut Latte Sachets 10pcs", "price": 78.00, "cost": 48.00, "cat": "Drinks", "img": "🥜"},
            {"name": "Coconut Water Natural 330ml", "price": 29.00, "cost": 18.00, "cat": "Drinks", "img": "🥥"},
            {"name": "Berry Fruit Punch 1L", "price": 45.00, "cost": 28.00, "cat": "Drinks", "img": "🫐"},
            {"name": "Chai Masala Tea 250g", "price": 85.00, "cost": 52.00, "cat": "Drinks", "img": "🫖"},
            {"name": "Apple Juice No Sugar 1L", "price": 49.00, "cost": 31.00, "cat": "Drinks", "img": "🍎"},
            {"name": "Sports Electrolyte Drink 500ml", "price": 24.00, "cost": 14.50, "cat": "Drinks", "img": "🏃"},
            {"name": "Cold Brew Coffee Ready 250ml", "price": 38.00, "cost": 23.00, "cat": "Drinks", "img": "🧊"},
            {"name": "Herbal Chamomile Tea 25 Bags", "price": 55.00, "cost": 34.00, "cat": "Drinks", "img": "🌼"},

            # --- Personal Care ---
            {"name": "Hydrating Face Cream 50ml", "price": 125.00, "cost": 78.00, "cat": "Personal Care", "img": "🧴"},
            {"name": "Herbal Hair Conditioner 300ml", "price": 92.00, "cost": 58.00, "cat": "Personal Care", "img": "🧴"},
            {"name": "Fresh Breath Mouthwash 500ml", "price": 68.00, "cost": 42.00, "cat": "Personal Care", "img": "🦷"},
            {"name": "Aloe Vera Shower Gel 750ml", "price": 78.00, "cost": 49.00, "cat": "Personal Care", "img": "🚿"},
            {"name": "Nail Care Cuticle Oil 15ml", "price": 45.00, "cost": 27.00, "cat": "Personal Care", "img": "💅"},
            {"name": "SPF 50 Sunscreen Lotion 200ml", "price": 135.00, "cost": 88.00, "cat": "Personal Care", "img": "🧴"},
            {"name": "Charcoal Face Wash 150ml", "price": 72.00, "cost": 45.00, "cat": "Personal Care", "img": "🧼"},
            {"name": "Coconut Oil Hair Serum 100ml", "price": 88.00, "cost": 55.00, "cat": "Personal Care", "img": "🥥"},
            {"name": "Intensive Hand Cream 75ml", "price": 52.00, "cost": 32.00, "cat": "Personal Care", "img": "✋"},
            {"name": "Anti-Aging Eye Cream 30ml", "price": 148.00, "cost": 95.00, "cat": "Personal Care", "img": "👁️"},
            {"name": "Floral Body Mist 150ml", "price": 65.00, "cost": 40.00, "cat": "Personal Care", "img": "🌸"},
            {"name": "Whitening Deodorant Spray", "price": 58.00, "cost": 36.00, "cat": "Personal Care", "img": "🛡️"},

            # --- Health ---
            {"name": "Ibuprofen 400mg (10 Tablets)", "price": 32.00, "cost": 19.00, "cat": "Health", "img": "💊"},
            {"name": "Calcium + Vitamin D Tablets (60pcs)", "price": 110.00, "cost": 72.00, "cat": "Health", "img": "🦴"},
            {"name": "Cough Syrup Honey Lemon 150ml", "price": 68.00, "cost": 43.00, "cat": "Health", "img": "🍯"},
            {"name": "Bandage Strips 100pcs", "price": 28.00, "cost": 16.00, "cat": "Health", "img": "🩹"},
            {"name": "Probiotic Capsules 30pcs", "price": 135.00, "cost": 88.00, "cat": "Health", "img": "🦠"},
            {"name": "Allergy Relief Tablets (20pcs)", "price": 75.00, "cost": 48.00, "cat": "Health", "img": "🤧"},
            {"name": "Magnesium Citrate Powder 200g", "price": 98.00, "cost": 62.00, "cat": "Health", "img": "🥄"},
            {"name": "Digital Thermometer", "price": 89.00, "cost": 55.00, "cat": "Health", "img": "🌡️"},
            {"name": "Zinc 50mg Supplements (60pcs)", "price": 85.00, "cost": 52.00, "cat": "Health", "img": "🧪"},
            {"name": "Throat Lozenges Honey-Lemon (24pcs)", "price": 38.00, "cost": 23.00, "cat": "Health", "img": "🍬"},
            {"name": "Blood Pressure Monitor", "price": 245.00, "cost": 165.00, "cat": "Health", "img": "❤️"},
            {"name": "Immune Booster Elderberry Syrup", "price": 125.00, "cost": 80.00, "cat": "Health", "img": "🫐"},

            # --- Household ---
            {"name": "Glass Cleaner Spray 500ml", "price": 52.00, "cost": 32.00, "cat": "Household", "img": "🪟"},
            {"name": "Fabric Softener Floral 2L", "price": 95.00, "cost": 62.00, "cat": "Household", "img": "🌸"},
            {"name": "Stain Remover Gel 500ml", "price": 68.00, "cost": 42.00, "cat": "Household", "img": "🧼"},
            {"name": "Floor Cleaning Liquid 1L", "price": 75.00, "cost": 48.00, "cat": "Household", "img": "🧹"},
            {"name": "Dishwasher Tablets 60pcs", "price": 165.00, "cost": 105.00, "cat": "Household", "img": "🍽️"},
            {"name": "Air Freshener Lavender Spray", "price": 45.00, "cost": 27.00, "cat": "Household", "img": "🌿"},
            {"name": "Scouring Sponges 6pcs", "price": 35.00, "cost": 20.00, "cat": "Household", "img": "🧽"},
            {"name": "Oven & Grill Cleaner 500ml", "price": 82.00, "cost": 51.00, "cat": "Household", "img": "🔥"},
            {"name": "Paper Towel Rolls 6pcs", "price": 68.00, "cost": 42.00, "cat": "Household", "img": "🧻"},
            {"name": "Insect Repellent Spray 400ml", "price": 88.00, "cost": 55.00, "cat": "Household", "img": "🦟"},
            {"name": "Laundry Bleach 1L", "price": 42.00, "cost": 25.00, "cat": "Household", "img": "🧺"},
            {"name": "Microfiber Cleaning Cloths 4pcs", "price": 55.00, "cost": 34.00, "cat": "Household", "img": "🧼"},

            # --- Bakery & Fresh ---
            {"name": "Sourdough Loaf Fresh", "price": 42.00, "cost": 25.00, "cat": "Bakery & Fresh", "img": "🍞"},
            {"name": "Plain Bagels Pack (6pcs)", "price": 58.00, "cost": 36.00, "cat": "Bakery & Fresh", "img": "🥯"},
            {"name": "Cheddar Cheese Slices 200g", "price": 68.00, "cost": 45.00, "cat": "Bakery & Fresh", "img": "🧀"},
            {"name": "Greek Yogurt Natural 500g", "price": 52.00, "cost": 32.00, "cat": "Bakery & Fresh", "img": "🥛"},
            {"name": "Blueberry Muffins Pack (4pcs)", "price": 65.00, "cost": 40.00, "cat": "Bakery & Fresh", "img": "🫐"},
            {"name": "Fresh Bananas Bunch", "price": 28.00, "cost": 18.00, "cat": "Bakery & Fresh", "img": "🍌"},
            {"name": "Whole Grain Rolls (8pcs)", "price": 38.00, "cost": 22.00, "cat": "Bakery & Fresh", "img": "🥨"},
            {"name": "Strawberry Jam 370g", "price": 55.00, "cost": 34.00, "cat": "Bakery & Fresh", "img": "🍓"},
            {"name": "Cottage Cheese 250g", "price": 48.00, "cost": 29.00, "cat": "Bakery & Fresh", "img": "🥛"},
            {"name": "Avocado Pack (4pcs)", "price": 75.00, "cost": 48.00, "cat": "Bakery & Fresh", "img": "🥑"},
            {"name": "Cinnamon Raisin Bread", "price": 45.00, "cost": 27.00, "cat": "Bakery & Fresh", "img": "🍞"},
            {"name": "Fresh Tomatoes 1kg", "price": 35.00, "cost": 22.00, "cat": "Bakery & Fresh", "img": "🍅"},

            # --- Snacks & Sweets ---
            {"name": "Cheese Flavored Corn Puffs 150g", "price": 28.00, "cost": 17.00, "cat": "Snacks & Sweets", "img": "🧀"},
            {"name": "Milk Chocolate Bar 100g", "price": 38.00, "cost": 23.00, "cat": "Snacks & Sweets", "img": "🍫"},
            {"name": "Roasted Almonds 200g", "price": 95.00, "cost": 62.00, "cat": "Snacks & Sweets", "img": "🥜"},
            {"name": "Strawberry Jelly Beans 250g", "price": 45.00, "cost": 28.00, "cat": "Snacks & Sweets", "img": "🍓"},
            {"name": "Tortilla Chips Salsa 180g", "price": 32.00, "cost": 19.50, "cat": "Snacks & Sweets", "img": "🌮"},
            {"name": "Peanut Butter Cookies 12pcs", "price": 58.00, "cost": 36.00, "cat": "Snacks & Sweets", "img": "🍪"},
            {"name": "Dark Chocolate Covered Raisins", "price": 72.00, "cost": 46.00, "cat": "Snacks & Sweets", "img": "🍇"},
            {"name": "Wasabi Peas 150g", "price": 42.00, "cost": 26.00, "cat": "Snacks & Sweets", "img": "🌱"},
            {"name": "Caramel Popcorn Family Pack", "price": 65.00, "cost": 41.00, "cat": "Snacks & Sweets", "img": "🍿"},
            {"name": "Hazelnut Spread 350g", "price": 88.00, "cost": 55.00, "cat": "Snacks & Sweets", "img": "🥜"},
            {"name": "Sour Candy Strips Mix", "price": 35.00, "cost": 21.00, "cat": "Snacks & Sweets", "img": "🍭"},
            {"name": "Pistachio Nuts Roasted 180g", "price": 105.00, "cost": 68.00, "cat": "Snacks & Sweets", "img": "🥜"},

            # --- Baby Care ---
            {"name": "Hypoallergenic Baby Lotion 400ml", "price": 85.00, "cost": 54.00, "cat": "Baby Care", "img": "🧴"},
            {"name": "Size 5 Diapers Economy Pack (80pcs)", "price": 320.00, "cost": 225.00, "cat": "Baby Care", "img": "👶"},
            {"name": "Baby Hair Brush & Comb Set", "price": 48.00, "cost": 29.00, "cat": "Baby Care", "img": "🪮"},
            {"name": "Teething Gel Natural Relief", "price": 62.00, "cost": 39.00, "cat": "Baby Care", "img": "🦷"},
            {"name": "Baby Laundry Detergent 1L", "price": 98.00, "cost": 63.00, "cat": "Baby Care", "img": "🧺"},
            {"name": "Nappy Rash Cream 100g", "price": 75.00, "cost": 48.00, "cat": "Baby Care", "img": "🍼"},
            {"name": "Baby Bottle Brush Cleaner", "price": 35.00, "cost": 21.00, "cat": "Baby Care", "img": "🍼"},
            {"name": "Newborn Wipes Fragrance Free (120pcs)", "price": 68.00, "cost": 44.00, "cat": "Baby Care", "img": "🧻"},
            {"name": "Baby Feeding Bibs Pack (5pcs)", "price": 45.00, "cost": 27.00, "cat": "Baby Care", "img": "👕"},
            {"name": "Infant Formula Milk Stage 1 800g", "price": 285.00, "cost": 195.00, "cat": "Baby Care", "img": "🍼"},
            {"name": "Baby Nail Clippers Set", "price": 42.00, "cost": 25.00, "cat": "Baby Care", "img": "✂️"},
            {"name": "Gentle Baby Oil 200ml", "price": 72.00, "cost": 46.00, "cat": "Baby Care", "img": "🛢️"}
        ]
        
        for p in products_setup:
            # Match against the existing categories already inside your DB
            cat_obj = next((c for c in categories if c.name == p["cat"]), None)
            
            if cat_obj is None:
                print(f"⚠️ Category '{p['cat']}' not found in DB. Skipping product '{p['name']}'.")
                continue
            
            prod = Product(
                category_id=cat_obj.id,
                barcode=f"6222000{random.randint(10000, 99999)}",
                name=p["name"],
                brand="RetailIQ Brands",
                description=f"High quality selection from our {p['cat']} division.",
                price=Decimal(p["price"]),
                cost_price=Decimal(p["cost"]),
                stock_quantity=random.randint(35, 110),
                minimum_stock=12,
                shelf_location=f"Aisle-{random.randint(1, 5)}-Bay-{random.randint(1, 4)}",
                image_url=p["img"],
                status="active"
            )
            db.add(prod)
        db.commit()
        print("✅ Products table seeded successfully using your pre-existing categories!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding products: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_products()