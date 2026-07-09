from pydantic import BaseModel, Field
from datetime import date


class ProfitPredictionRequest(BaseModel):
    # Categorical fields matching training pipeline requirements
    ship_mode: str = Field(..., alias="Ship Mode", description="e.g., Standard Class, Second Class, First Class")
    segment: str = Field(..., alias="Segment", description="e.g., Consumer, Corporate, Home Office")
    country: str = Field("United States", alias="Country")
    city: str = Field(..., alias="City")
    state: str = Field(..., alias="State")
    region: str = Field(..., alias="Region")
    category: str = Field(..., alias="Category", description="e.g., Furniture, Office Supplies, Technology")
    sub_category: str = Field(..., alias="Sub-Category")
    
    # Date markers used to extract time components
    order_date: date = Field(..., alias="Order Date")
    ship_date: date = Field(..., alias="Ship Date")
    
    # Continuous numeric fields crucial for profit assessment
    sales: float = Field(..., alias="Sales", description="Total sales volume value")
    quantity: int = Field(..., alias="Quantity", description="Quantity ordered")
    discount: float = Field(..., alias="Discount", description="Discount multiplier applied (e.g., 0.2)")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Ship Mode": "Second Class",
                "Segment": "Consumer",
                "Country": "United States",
                "City": "Henderson",
                "State": "Kentucky",
                "Region": "South",
                "Category": "Furniture",
                "Sub-Category": "Bookcases",
                "Order Date": "2026-07-09",
                "Ship Date": "2026-07-12",
                "Sales": 261.96,
                "Quantity": 2,
                "Discount": 0.00
            }
        }

class ProfitPredictionResponse(BaseModel):
    predicted_profit: float