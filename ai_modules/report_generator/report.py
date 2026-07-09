"""
Turns a KPI dict (produced by app/services/report_service.compute_kpis) into
the structured prompt the LLM expects, then returns the generated narrative.
Adapted from notebook cell 5 — same rules/output structure, but the numbers
are injected dynamically instead of hardcoded.
"""
from ai_modules.report_generator.llm_summary import generate_report_text
 
 
def _fmt_money(value: float) -> str:
    return f"{value:,.2f}"
 
 
def build_prompt(kpis: dict) -> str:
    """
    Expected keys in kpis (see report_service.compute_kpis):
      total_revenue, completed_revenue, completion_rate, avg_order_value,
      average_rating, category_revenue (dict), top_products (dict),
      weak_products (dict), country_revenue (dict), payment_status (dict)
    """
    category_lines = "\n".join(
        f"{name}: {_fmt_money(value)}"
        for name, value in kpis.get("category_revenue", {}).items()
    ) or "N/A"
 
    top_products_lines = "\n".join(
        f"{name}: {_fmt_money(value)}"
        for name, value in kpis.get("top_products", {}).items()
    ) or "N/A"
 
    weak_products_lines = "\n".join(
        f"{name}: {qty}" for name, qty in kpis.get("weak_products", {}).items()
    ) or "N/A"
 
    country_lines = "\n".join(
        f"{name}: {_fmt_money(value)}"
        for name, value in kpis.get("country_revenue", {}).items()
    ) or "N/A"
 
    payment_lines = "\n".join(
        f"{status}: {count}" for status, count in kpis.get("payment_status", {}).items()
    ) or "N/A"
 
    prompt = f"""
You are a Senior Business Intelligence Analyst.
 
You MUST follow these rules strictly:
- Use ONLY the provided numbers.
- Do NOT generate trends (YoY, growth, increase) unless explicitly given.
- Every insight MUST include a number or computed comparison from the data.
- No vague business statements.
- No assumptions.
 
BUSINESS DATA
 
Total Revenue: {_fmt_money(kpis['total_revenue'])}
Completed Revenue: {_fmt_money(kpis['completed_revenue'])}
Completion Rate: {kpis['completion_rate']:.2f}%
Average Order Value: {_fmt_money(kpis['avg_order_value'])}
Average Rating: {kpis.get('average_rating', 0):.2f}
 
CATEGORY REVENUE:
{category_lines}
 
TOP PRODUCTS (Revenue):
{top_products_lines}
 
WEAK PRODUCTS (Quantity):
{weak_products_lines}
 
COUNTRY REVENUE:
{country_lines}
 
PAYMENTS:
{payment_lines}
 
ANALYSIS RULES
 
1. Always compare values (e.g., Country A vs Country B difference = X).
2. Always rank (Top 1, Top 2... clearly).
3. Always quantify gaps (difference or percentage if possible).
4. Never use generic phrases like "strong performance".
5. Every insight must reference a number explicitly.
 
OUTPUT STRUCTURE
 
Executive Summary
- ONLY 2 paragraphs
- Must include 2-3 numeric insights
 
Financial Performance
- Break down revenue vs completed revenue (difference must be calculated)
- Explain completion rate impact using numbers
- AOV interpretation with reasoning
 
Product Performance
- Rank top products with gaps between them
- Identify weakest products and quantify issue
- Compare category dominance (difference between top and second)
 
Regional Performance
- Rank countries
- Show numeric gaps
- Identify concentration risk if top 2 > X%
 
Risks
- Must be based on numeric thresholds only
 
Recommendations
- 5-7 actionable ONLY
"""
    return prompt.strip()
 
 
def generate_narrative(kpis: dict) -> str:
    """Public entry point used by app/services/report_service.py"""
    prompt = build_prompt(kpis)
    return generate_report_text(prompt)
 