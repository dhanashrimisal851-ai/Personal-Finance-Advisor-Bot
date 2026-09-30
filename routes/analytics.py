from datetime import date
from flask import Blueprint, render_template, request, jsonify, session
from sqlalchemy import extract, func
from models import db, Income, Expense
from routes.auth import login_required
from utils.calculations import (
    get_monthly_finances,
    get_category_breakdown,
    calculate_financial_health_score,
    safe_div
)

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics")
@login_required
def analytics_view():
    return render_template("analytics.html")

@analytics_bp.route("/api/analytics", methods=["GET"])
@login_required
def get_analytics():
    user_id = session["user_id"]
    today = date.today()
    try:
        month = int(request.args.get("month", today.month))
        year = int(request.args.get("year", today.year))
    except ValueError:
        month, year = today.month, today.year

    # 1. Current Month Finances & Category Distribution
    current_finances = get_monthly_finances(user_id, month, year)
    current_breakdown = get_category_breakdown(user_id, month, year)

    # 2. Previous Month Finances & Category Distribution (for comparison)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_finances = get_monthly_finances(user_id, prev_month, prev_year)
    prev_breakdown = get_category_breakdown(user_id, prev_month, prev_year)
    prev_breakdown_map = {item["category"]: item["amount"] for item in prev_breakdown}

    # Compare categories between current and previous month
    comparison = []
    # All distinct categories across both months
    all_cats = list(dict.fromkeys([b["category"] for b in current_breakdown] + list(prev_breakdown_map.keys())))
    for cat in all_cats:
        curr_amt = next((b["amount"] for b in current_breakdown if b["category"] == cat), 0.0)
        prev_amt = prev_breakdown_map.get(cat, 0.0)
        diff = curr_amt - prev_amt
        pct_change = safe_div(diff, prev_amt) * 100 if prev_amt > 0 else (100.0 if curr_amt > 0 else 0.0)
        comparison.append({
            "category": cat,
            "current_amount": round(curr_amt, 2),
            "previous_amount": round(prev_amt, 2),
            "difference": round(diff, 2),
            "percentage_change": round(pct_change, 1)
        })

    # 3. Monthly 6-Month Trend Data (Bar & Line chart)
    # Generate past 6 months timeline ending at selected month/year
    trend_labels = []
    income_trend = []
    expense_trend = []
    savings_trend = []

    m, y = month, year
    months_list = []
    for _ in range(6):
        months_list.append((m, y))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months_list.reverse()

    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for (m_idx, y_idx) in months_list:
        trend_labels.append(f"{month_names[m_idx]} {y_idx}")
        m_fin = get_monthly_finances(user_id, m_idx, y_idx)
        income_trend.append(m_fin["total_income"])
        expense_trend.append(m_fin["total_expense"])
        savings_trend.append(m_fin["total_savings"])

    # 4. Top Spending Categories with explanation
    top_categories = current_breakdown[:5]

    # 5. Financial Health Score
    health_score = calculate_financial_health_score(user_id, month, year)

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "current_finances": current_finances,
        "previous_finances": prev_finances,
        "category_distribution": current_breakdown,
        "category_comparison": comparison,
        "top_spending": top_categories,
        "trends": {
            "labels": trend_labels,
            "income": income_trend,
            "expenses": expense_trend,
            "savings": savings_trend
        },
        "health_score": health_score
    })
