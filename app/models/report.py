"""
SQLAlchemy model for tracking generated business reports (status, file
location, date range). New file — your app/models/ folder didn't have one.
 
After adding this file:
  1. Import it in app/models/__init__.py so Alembic/metadata picks it up:
        from app.models.report import Report
  2. Run the migration in database/migrations/migration_reports.sql
     (or add the CREATE TABLE to database/schema.sql, matching your existing
     convention for shelf_monitoring).
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database import Base  # adjust if your declarative Base lives elsewhere
 
 
class Report(Base):
    __tablename__ = "reports"
 
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False, default="custom")  # daily/weekly/monthly/custom
    date_from = Column(DateTime, nullable=False)
    date_to = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending/generating/completed/failed
    file_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=True)  # FK to users.id, if you want to track who requested it
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)