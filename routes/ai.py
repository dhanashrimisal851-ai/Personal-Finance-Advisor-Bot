import os
from datetime import date
from flask import Blueprint, render_template, request, jsonify, session
from models import db, SavingsGoal, Budget
from routes.auth import login_required
from utils.calculations import (
    get_monthly_finances,
    get_category_breakdown,
    get_budget_performance
)
from services.gemini_service import (
    generate_ai_budget_plan,
    get_ai_financial_advice,
    get_gemini_client
)
from config import Config

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai-advisor")
@login_required
def ai_advisor_view():
    return render_template("ai_advisor.html")

@ai_bp.route("/api/ai/status", methods=["GET"])
@login_required
def ai_status():
    api_key = os.getenv("GEMINI_API_KEY") or Config.GEMINI_API_KEY
    is_live = bool(api_key and not api_key.startswith("your_"))
    return jsonify({
        "success": True,
        "is_live_gemini": is_live,
        "engine": "Google Gemini 1.5/2.5 Flash" if is_live else "Smart Financial Advisor Engine (Offline Heuristic Mode)",
        "model": "gemini-1.5-flash" if is_live else "Intelligent Heuristic Fallback"
    })

@ai_bp.route("/api/ai/advice", methods=["POST"])
@login_required
def ask_advice():
    user_id = session["user_id"]
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Please enter a question for the AI Advisor."}), 400

    today = date.today()
    month = today.month
    year = today.year

    # Aggregate financial context for the AI
    finances = get_monthly_finances(user_id, month, year)
    categories = get_category_breakdown(user_id, month, year)
    budget_perf = get_budget_performance(user_id, month, year)
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    context = {
        "total_income": finances["total_income"],
        "total_expense": finances["total_expense"],
        "total_savings": finances["total_savings"],
        "savings_rate": finances["savings_rate"],
        "top_categories": categories[:4],
        "overspent_categories": budget_perf["overspent_categories"],
        "goals": [{"name": g.name, "target_amount": g.target_amount, "current_amount": g.current_amount} for g in goals]
    }

    try:
        advice_response = get_ai_financial_advice(question, context)
        return jsonify({
            "success": True,
            "question": question,
            "data": advice_response
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate advice: {str(e)}"}), 500

@ai_bp.route("/api/ai/generate-budget", methods=["POST"])
@login_required
def generate_budget():
    data = request.get_json() or {}

    try:
        income = float(data.get("income", 0))
        fixed_expenses = float(data.get("fixed_expenses", 0))
        variable_expenses = float(data.get("variable_expenses", 0))
        savings_pct = float(data.get("savings_percentage", 20))
        goal = (data.get("goal") or "Financial Security").strip()
    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid numerical values for income and expenses."}), 400

    if income <= 0:
        return jsonify({"error": "Monthly income must be greater than zero."}), 400

    try:
        budget_plan = generate_ai_budget_plan(income, fixed_expenses, variable_expenses, goal, savings_pct)
        return jsonify({
            "success": True,
            "plan": budget_plan
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate AI budget plan: {str(e)}"}), 500
