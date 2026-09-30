import math
from datetime import date, datetime
from flask import Blueprint, render_template, request, jsonify, session
from models import db, SavingsGoal
from routes.auth import login_required
from utils.validators import validate_positive_number, validate_non_negative_number, parse_date

goals_bp = Blueprint("goals", __name__)

@goals_bp.route("/goals")
@login_required
def goals_view():
    return render_template("goals.html")

@goals_bp.route("/api/goals", methods=["GET"])
@login_required
def get_goals():
    user_id = session["user_id"]
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.id.desc()).all()
    
    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_progress = round((total_saved / total_target * 100), 1) if total_target > 0 else 0.0

    return jsonify({
        "success": True,
        "goals": [g.to_dict() for g in goals],
        "summary": {
            "total_target": round(total_target, 2),
            "total_saved": round(total_saved, 2),
            "overall_progress": overall_progress,
            "goals_count": len(goals)
        }
    })

@goals_bp.route("/api/goals", methods=["POST"])
@login_required
def add_goal():
    user_id = session["user_id"]
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Goal name is required."}), 400

    valid_t, target_amount = validate_positive_number(data.get("target_amount"))
    if not valid_t:
        return jsonify({"error": "Target amount must be a positive number."}), 400

    valid_c, current_amount = validate_non_negative_number(data.get("current_amount", 0))
    target_date = parse_date(data.get("target_date"))
    description = (data.get("description") or "").strip()

    try:
        goal = SavingsGoal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            description=description
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({"success": True, "message": f"Goal '{name}' created successfully!", "goal": goal.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save goal: {str(e)}"}), 500

@goals_bp.route("/api/goals/<int:goal_id>", methods=["PUT"])
@login_required
def update_goal(goal_id):
    user_id = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return jsonify({"error": "Goal not found."}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"].strip():
        goal.name = data["name"].strip()

    if "target_amount" in data:
        valid_t, target_amount = validate_positive_number(data["target_amount"])
        if not valid_t:
            return jsonify({"error": "Target amount must be positive."}), 400
        goal.target_amount = target_amount

    if "current_amount" in data:
        valid_c, current_amount = validate_non_negative_number(data["current_amount"])
        if not valid_c:
            return jsonify({"error": "Current amount cannot be negative."}), 400
        goal.current_amount = current_amount

    if "target_date" in data:
        goal.target_date = parse_date(data["target_date"])

    if "description" in data:
        goal.description = (data["description"] or "").strip()

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Goal updated successfully!", "goal": goal.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update goal: {str(e)}"}), 500

@goals_bp.route("/api/goals/<int:goal_id>/contribute", methods=["POST"])
@login_required
def contribute_to_goal(goal_id):
    """Add extra funds to a goal."""
    user_id = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return jsonify({"error": "Goal not found."}), 404

    data = request.get_json() or {}
    valid_amt, amount = validate_positive_number(data.get("amount"))
    if not valid_amt:
        return jsonify({"error": "Please enter a valid positive deposit amount."}), 400

    goal.current_amount += amount
    try:
        db.session.commit()
        return jsonify({"success": True, "message": f"Added ₹{amount:,.0f} to '{goal.name}'!", "goal": goal.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to record contribution: {str(e)}"}), 500

@goals_bp.route("/api/goals/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id):
    user_id = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return jsonify({"error": "Goal not found."}), 404

    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"success": True, "message": "Goal deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete goal: {str(e)}"}), 500

@goals_bp.route("/api/goals/calculator", methods=["POST"])
@login_required
def savings_calculator():
    """
    Savings Calculator:
    Inputs: Goal Amount, Current Savings, Monthly Contribution, Target Date
    Computes: Remaining amount, required monthly saving, estimated completion months & date.
    """
    data = request.get_json() or {}
    valid_goal, goal_amount = validate_positive_number(data.get("goal_amount"))
    if not valid_goal:
        return jsonify({"error": "Goal amount must be greater than 0."}), 400

    valid_curr, current_savings = validate_non_negative_number(data.get("current_savings", 0))
    monthly_contrib = float(data.get("monthly_contribution", 0) or 0)
    target_date_str = data.get("target_date")
    target_dt = parse_date(target_date_str) if target_date_str else None

    remaining_amount = max(0.0, goal_amount - current_savings)

    # If target date provided, calculate required monthly savings
    today = date.today()
    required_monthly = None
    months_until_target = None

    if target_dt and target_dt > today:
        days = (target_dt - today).days
        months_until_target = max(1, round(days / 30.4))
        required_monthly = round(remaining_amount / months_until_target, 2)

    # If monthly contribution provided, calculate estimated months & completion date
    estimated_months = None
    estimated_date = None
    if monthly_contrib > 0:
        estimated_months = math.ceil(remaining_amount / monthly_contrib)
        target_year = today.year + (today.month + estimated_months - 1) // 12
        target_month = (today.month + estimated_months - 1) % 12 + 1
        calc_dt = date(target_year, target_month, 1)
        estimated_date = calc_dt.strftime("%B %Y")
    
    return jsonify({
        "success": True,
        "calculation": {
            "goal_amount": goal_amount,
            "current_savings": current_savings,
            "remaining_amount": round(remaining_amount, 2),
            "monthly_contribution": monthly_contrib,
            "months_until_target": months_until_target,
            "required_monthly_savings": required_monthly,
            "estimated_months_to_complete": estimated_months,
            "estimated_completion_date": estimated_date
        }
    })
