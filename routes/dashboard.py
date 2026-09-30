from datetime import date
from flask import Blueprint, render_template, jsonify, session, request
from models import db, Income, Expense, Budget, SavingsGoal
from routes.auth import login_required
from utils.calculations import (
    get_monthly_finances,
    get_budget_performance,
    get_category_breakdown,
    calculate_financial_health_score,
    generate_financial_alerts
)

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard_view():
    return render_template("dashboard.html")

@dashboard_bp.route("/api/dashboard", methods=["GET"])
@login_required
def api_dashboard():
    user_id = session["user_id"]
    today = date.today()

    try:
        month = int(request.args.get("month", today.month))
        year = int(request.args.get("year", today.year))
    except ValueError:
        month, year = today.month, today.year

    finances = get_monthly_finances(user_id, month, year)
    budget_perf = get_budget_performance(user_id, month, year)
    category_breakdown = get_category_breakdown(user_id, month, year)
    health_score = calculate_financial_health_score(user_id, month, year)
    alerts = generate_financial_alerts(user_id, month, year)

    # Fetch recent transactions (last 6 items across income & expense)
    recent_incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc(), Income.id.desc()).limit(6).all()
    recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc(), Expense.id.desc()).limit(6).all()

    txs = []
    for inc in recent_incomes:
        txs.append({
            "id": inc.id,
            "type": "Income",
            "category": inc.source,
            "description": inc.description or inc.source,
            "amount": inc.amount,
            "date": inc.date.strftime("%Y-%m-%d"),
            "payment_method": "Bank"
        })
    for exp in recent_expenses:
        txs.append({
            "id": exp.id,
            "type": "Expense",
            "category": exp.category,
            "description": exp.description or exp.category,
            "amount": exp.amount,
            "date": exp.date.strftime("%Y-%m-%d"),
            "payment_method": exp.payment_method
        })

    # Sort combined transactions by date desc
    txs.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
    recent_transactions = txs[:8]

    # Active savings goals
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()
    goals_data = [g.to_dict() for g in goals]

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "finances": {
            "monthly_income": finances["total_income"],
            "total_expenses": finances["total_expense"],
            "current_savings": finances["total_savings"],
            "savings_percentage": finances["savings_rate"],
            "remaining_budget": budget_perf["remaining_budget"]
        },
        "budget_performance": budget_perf,
        "category_breakdown": category_breakdown,
        "health_score": health_score,
        "alerts": alerts,
        "recent_transactions": recent_transactions,
        "goals": goals_data
    })
