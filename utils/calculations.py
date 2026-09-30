from datetime import date
from sqlalchemy import extract, func
from models import db, Income, Expense, Budget, SavingsGoal

def safe_div(num: float, den: float, default: float = 0.0) -> float:
    if den == 0 or den is None:
        return default
    return num / den

def get_monthly_finances(user_id: int, month: int, year: int):
    """Calculate total income, expenses, savings, and savings rate for a user in a given month/year."""
    # Income sum
    income_query = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == user_id,
        extract("month", Income.date) == month,
        extract("year", Income.date) == year
    ).scalar()
    total_income = float(income_query or 0.0)

    # Expense sum
    expense_query = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == user_id,
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year
    ).scalar()
    total_expense = float(expense_query or 0.0)

    total_savings = total_income - total_expense
    savings_rate = safe_div(total_savings, total_income, 0.0) * 100 if total_income > 0 else 0.0

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_savings": round(total_savings, 2),
        "savings_rate": max(-100.0, min(100.0, round(savings_rate, 1)))
    }

def get_category_breakdown(user_id: int, month: int, year: int):
    """Returns category-wise expenses for month/year."""
    results = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label("total")
    ).filter(
        Expense.user_id == user_id,
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    total_exp = sum(r.total for r in results) if results else 0.0
    breakdown = []
    for cat, amt in results:
        amt = float(amt)
        pct = safe_div(amt, total_exp) * 100 if total_exp > 0 else 0.0
        breakdown.append({
            "category": cat,
            "amount": round(amt, 2),
            "percentage": round(pct, 1)
        })
    return breakdown

def get_budget_performance(user_id: int, month: int, year: int):
    """Calculates budget adherence, remaining amounts, and alert levels for month/year."""
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    
    # Get actual spending per category in this month/year
    spending_results = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label("spent")
    ).filter(
        Expense.user_id == user_id,
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year
    ).group_by(Expense.category).all()

    spending_map = {row.category: float(row.spent) for row in spending_results}
    
    performance_list = []
    total_budgeted = 0.0
    total_spent_budgeted = 0.0
    overspent_categories = []
    warning_categories = []

    for b in budgets:
        spent = spending_map.get(b.category, 0.0)
        remaining = b.amount - spent
        usage_pct = safe_div(spent, b.amount) * 100 if b.amount > 0 else 0.0
        total_budgeted += b.amount
        total_spent_budgeted += spent

        if usage_pct >= 90:
            status = "danger"
            status_text = "Overspending Alert"
            overspent_categories.append(b.category)
        elif usage_pct >= 70:
            status = "warning"
            status_text = "Warning"
            warning_categories.append(b.category)
        else:
            status = "normal"
            status_text = "Normal"

        performance_list.append({
            "id": b.id,
            "category": b.category,
            "budget": round(b.amount, 2),
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": round(usage_pct, 1),
            "status": status,
            "status_text": status_text
        })

    remaining_budget = total_budgeted - total_spent_budgeted

    return {
        "items": performance_list,
        "total_budgeted": round(total_budgeted, 2),
        "total_spent_budgeted": round(total_spent_budgeted, 2),
        "remaining_budget": round(remaining_budget, 2),
        "overspent_count": len(overspent_categories),
        "overspent_categories": overspent_categories,
        "warning_categories": warning_categories
    }

def calculate_financial_health_score(user_id: int, month: int, year: int):
    """
    Computes a transparent 0-100 financial health score based on:
    - Savings rate (up to 30 pts)
    - Budget adherence / overspending (up to 30 pts)
    - Expense-to-income ratio (up to 25 pts)
    - Savings goals progress (up to 15 pts)
    """
    finances = get_monthly_finances(user_id, month, year)
    budget_perf = get_budget_performance(user_id, month, year)
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    income = finances["total_income"]
    expense = finances["total_expense"]
    savings_rate = finances["savings_rate"]

    score = 0
    positive_habits = []
    areas_to_improve = []

    # 1. Savings Rate (30 pts)
    if savings_rate >= 30:
        score += 30
        positive_habits.append(f"Excellent savings rate of {savings_rate:.1f}% (above 30% benchmark).")
    elif savings_rate >= 20:
        score += 24
        positive_habits.append(f"Solid savings rate of {savings_rate:.1f}%.")
    elif savings_rate >= 10:
        score += 16
        areas_to_improve.append("Aim to lift your savings rate above 20% for stronger wealth building.")
    elif savings_rate > 0:
        score += 8
        areas_to_improve.append(f"Low savings rate ({savings_rate:.1f}%). Look for non-essential spending to trim.")
    else:
        score += 0
        areas_to_improve.append("Expenses currently equal or exceed income. Prioritize a deficit elimination plan.")

    # 2. Budget Adherence (30 pts)
    if not budget_perf["items"]:
        # No budgets set yet
        score += 15
        areas_to_improve.append("Set category budgets to unlock granular tracking and alerts.")
    else:
        overspent = budget_perf["overspent_count"]
        if overspent == 0:
            score += 30
            positive_habits.append("All category budgets are well maintained within safe limits.")
        elif overspent == 1:
            score += 20
            areas_to_improve.append(f"Overspending in 1 category ({', '.join(budget_perf['overspent_categories'])}).")
        elif overspent == 2:
            score += 10
            areas_to_improve.append(f"Overspending in 2 categories ({', '.join(budget_perf['overspent_categories'])}).")
        else:
            score += 0
            areas_to_improve.append(f"Multiple categories exceeded budget ({', '.join(budget_perf['overspent_categories'])}).")

    # 3. Expense to Income Ratio (25 pts)
    if income > 0:
        ratio = (expense / income) * 100
        if ratio <= 50:
            score += 25
            positive_habits.append(f"Frugal lifestyle: living on only {ratio:.1f}% of income.")
        elif ratio <= 70:
            score += 20
            positive_habits.append(f"Healthy expense-to-income ratio ({ratio:.1f}%).")
        elif ratio <= 90:
            score += 12
            areas_to_improve.append(f"High expense ratio ({ratio:.1f}%). Tight buffer for unexpected costs.")
        else:
            score += 4
            areas_to_improve.append(f"Living paycheck-to-paycheck ({ratio:.1f}% of income spent).")
    else:
        score += 10
        areas_to_improve.append("Add your monthly income to evaluate your expense-to-income balance.")

    # 4. Savings Goals Progress (15 pts)
    if goals:
        avg_progress = sum(g.progress_percentage for g in goals) / len(goals)
        if avg_progress >= 50:
            score += 15
            positive_habits.append(f"Active savings momentum: {avg_progress:.1f}% achieved across goals.")
        elif avg_progress >= 20:
            score += 10
            positive_habits.append("Consistent progress made towards your savings targets.")
        else:
            score += 6
            areas_to_improve.append("Keep contributing towards your savings goals to build financial security.")
    else:
        score += 5
        areas_to_improve.append("Create a savings goal (e.g. emergency fund or major purchase) to stay motivated.")

    # Cap score between 0 and 100
    final_score = max(0, min(100, score))

    if final_score >= 80:
        badge = "Excellent"
        summary = "Your financial health is strong with disciplined spending and solid savings habits."
    elif final_score >= 60:
        badge = "Good"
        summary = "You are on the right track, with balanced cash flows and room for strategic optimization."
    elif final_score >= 40:
        badge = "Moderate"
        summary = "Your budget has vulnerabilities. Reining in top expenses can rapidly improve your score."
    else:
        badge = "Needs Attention"
        summary = "Spending pressure is elevated. Focusing on emergency savings and budget limits is recommended."

    return {
        "score": final_score,
        "badge": badge,
        "summary": summary,
        "positive_habits": positive_habits,
        "areas_to_improve": areas_to_improve,
        "disclaimer": "This score is an educational metric calculated from your recorded budgets and cash flow, not a certified financial audit."
    }

def generate_financial_alerts(user_id: int, month: int, year: int):
    """Generates intelligent in-app notifications and alerts for the user."""
    alerts = []
    budget_perf = get_budget_performance(user_id, month, year)
    finances = get_monthly_finances(user_id, month, year)
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    # 1. Overspending alerts
    for b in budget_perf["items"]:
        if b["percentage"] >= 90:
            alerts.append({
                "type": "danger",
                "icon": "exclamation-triangle",
                "title": "Overspending Alert",
                "message": f"You have used {b['percentage']:.1f}% of your {b['category']} budget (₹{b['spent']:,.0f} of ₹{b['budget']:,.0f})."
            })
        elif b["percentage"] >= 70:
            alerts.append({
                "type": "warning",
                "icon": "exclamation-circle",
                "title": "Budget Warning",
                "message": f"You are approaching your limit on {b['category']} ({b['percentage']:.1f}% used)."
            })

    # 2. Savings goal alerts
    for g in goals:
        if g.remaining_amount <= 2000 and g.remaining_amount > 0:
            alerts.append({
                "type": "info",
                "icon": "trophy",
                "title": "Goal Almost Reached!",
                "message": f"You are only ₹{g.remaining_amount:,.0f} away from your '{g.name}' target!"
            })
        elif g.progress_percentage >= 100:
            alerts.append({
                "type": "success",
                "icon": "check-circle",
                "title": "Goal Achieved!",
                "message": f"Congratulations! You fully reached your '{g.name}' goal of ₹{g.target_amount:,.0f}."
            })

    # 3. Positive feedback
    if finances["savings_rate"] >= 25:
        alerts.append({
            "type": "success",
            "icon": "award",
            "title": "Great Saving Habit",
            "message": f"You saved {finances['savings_rate']:.1f}% of your income this month! Keep up the momentum."
        })

    return alerts
