"""
Orchestrates business report generation:
  1. Computes KPIs from the database (pandas, replaces notebook cells 0-1)
  2. Generates the executive narrative via the LLM
  3. Renders everything to PDF
  4. Persists a Report row and returns it

*** ADJUST BEFORE RUNNING ***
_load_sales_frame() assumes tables/columns based on your models/ folder:
  customers(id, name, country, email)
  products(id, name, category_id, price)
  categories(id, name)
  purchases(id, customer_id, product_id, quantity, unit_price,
            purchase_date, payment_status, payment_method)
If your actual database/schema.sql uses different table or column names
(e.g. separate orders/order_items tables), update the SQL below to match —
everything downstream (compute_kpis, the LLM prompt, the PDF) is agnostic
to where the numbers came from.
"""
import os
import uuid
from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from ai_modules.report_generator.pdf_generator import generate_pdf
from ai_modules.report_generator.report import generate_narrative
from app.models.report import Report

REPORTS_DIR = "storage/reports"


def _load_sales_frame(db: Session, date_from: datetime, date_to: datetime) -> dict:
    engine = db.get_bind()

    order_items = pd.read_sql(
        text("""
            SELECT oi.*, o.customer_id, o.status AS payment_status,
                   o.payment_method, o.created_at AS purchase_date
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.created_at BETWEEN :date_from AND :date_to
        """),
        engine,
        params={"date_from": date_from, "date_to": date_to},
    )
    products = pd.read_sql("SELECT * FROM products", engine)
    categories = pd.read_sql("SELECT * FROM categories", engine)
    customers = pd.read_sql(
        "SELECT * FROM users WHERE role = 'customer'", engine
    )

    order_items["revenue"] = order_items["quantity"] * order_items["unit_price"]

    sales = order_items.merge(
        products, left_on="product_id", right_on="id", how="left", suffixes=("", "_product")
    )
    sales = sales.merge(
        categories, left_on="category_id", right_on="id", how="left", suffixes=("", "_category")
    )
    sales = sales.merge(
        customers, left_on="customer_id", right_on="id", how="left", suffixes=("", "_customer")
    )

    return {"sales": sales, "purchases": order_items}


def compute_kpis(db: Session, date_from: datetime, date_to: datetime) -> dict:
    """Replaces notebook cell 1 (KPI ENGINE)."""
    frames = _load_sales_frame(db, date_from, date_to)
    sales = frames["sales"]
    purchases = frames["purchases"]

    if sales.empty:
        raise ValueError("No sales data found for the selected date range.")

    total_revenue = float(sales["revenue"].sum())
    completed_revenue = float(
        sales.loc[sales["payment_status"] == "completed", "revenue"].sum()
    )
    total_orders = int(purchases["id"].nunique())
    avg_order_value = total_revenue / total_orders if total_orders else 0.0
    completion_rate = (
        float(purchases["payment_status"].eq("completed").mean() * 100)
        if total_orders else 0.0
    )

    top_products = (
        sales.groupby("name")["revenue"].sum().sort_values(ascending=False).head(5).to_dict()
    )
    weak_products = (
        sales.groupby("name")["quantity"].sum().sort_values().head(5).to_dict()
    )
    category_revenue = (
        sales.groupby("name_category")["revenue"].sum().sort_values(ascending=False).to_dict()
        if "name_category" in sales.columns else {}
    )
    country_revenue = (
        sales.groupby("country")["revenue"].sum().sort_values(ascending=False).to_dict()
        if "country" in sales.columns else {}
    )
    payment_status = purchases["payment_status"].value_counts().to_dict()

    return {
        "total_revenue": total_revenue,
        "completed_revenue": completed_revenue,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "completion_rate": completion_rate,
        "average_rating": 0.0,  # TODO: wire up once a reviews table/model exists
        "top_products": top_products,
        "weak_products": weak_products,
        "category_revenue": category_revenue,
        "country_revenue": country_revenue,
        "payment_status": payment_status,
    }


def create_report(
    db: Session,
    title: str,
    date_from: datetime,
    date_to: datetime,
    report_type: str = "custom",
    created_by: Optional[int] = None,
) -> Report:
    """
    Full pipeline: KPIs -> LLM narrative -> PDF -> Report row.
    Runs synchronously for now. LLM inference is slow (seconds to minutes on
    CPU) — move this to a background task / job queue once this is used at
    scale, so the HTTP request doesn't block on it.
    """
    report = Report(
        title=title,
        report_type=report_type,
        date_from=date_from,
        date_to=date_to,
        status="generating",
        created_by=created_by,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    try:
        kpis = compute_kpis(db, date_from, date_to)
        narrative = generate_narrative(kpis)

        os.makedirs(REPORTS_DIR, exist_ok=True)
        filename = f"report_{report.id}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)

        generate_pdf(
            output_path=output_path,
            narrative=narrative,
            total_revenue=kpis["total_revenue"],
            completed_revenue=kpis["completed_revenue"],
            completion_rate=kpis["completion_rate"],
            avg_order_value=kpis["avg_order_value"],
            average_rating=kpis["average_rating"],
        )

        report.status = "completed"
        report.file_path = output_path
        report.completed_at = datetime.utcnow()

    except Exception as exc:  # noqa: BLE001 — surface any failure on the Report row
        report.status = "failed"
        report.error_message = str(exc)

    db.commit()
    db.refresh(report)
    return report


def get_report(db: Session, report_id: int) -> Optional[Report]:
    return db.query(Report).filter(Report.id == report_id).first()


def list_reports(db: Session, limit: int = 50) -> list[Report]:
    return db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()