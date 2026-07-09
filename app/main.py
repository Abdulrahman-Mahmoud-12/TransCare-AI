from fastapi import FastAPI
from app.database import engine, Base
from fastapi.staticfiles import StaticFiles

from app.models.user import User
from app.models.product import Product
from app.models.customer import CustomerAnalytics
from app.routers import home, auth, customer, admin, assistant, shelf_monitoring, forcasting, reports

# Initialize FastAPI app instance
app = FastAPI(
    title="RetailIQ — Smart Retail System",
    description="Backend API ecosystem for shelf monitoring, forecasting, and RAG assistant workflows.",
    version="1.0.0"
)

# Mount the static files directory so your CSS, JS, and image assets serve properly
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.on_event("startup")
def configure_database_tables():
    """
    Guards execution by automatically binding metadata schemas 
    and auto-generating missing local tables during development loops.
    """
    Base.metadata.create_all(bind=engine)

# Include Routers
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(admin.router)
app.include_router(assistant.router)
app.include_router(shelf_monitoring.router)
app.include_router(forcasting.router)
app.include_router(reports.router)