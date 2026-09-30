import os
from flask import Blueprint, render_template, request, jsonify, session
from models import db, User, Income, Expense, Budget, SavingsGoal, FinancialReport
from routes.auth import login_required
from utils.seed_data import seed_demo_data

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings")
@login_required
def settings_view():
    user = User.query.get(session["user_id"])
    return render_template("settings.html", user=user)

@settings_bp.route("/api/settings/profile", methods=["POST"])
@login_required
def update_profile():
    user = User.query.get(session["user_id"])
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Full Name cannot be empty."}), 400

    user.name = name
    try:
        db.session.commit()
        session["user_name"] = user.name
        return jsonify({"success": True, "message": "Profile updated successfully!", "user": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500

@settings_bp.route("/api/settings/password", methods=["POST"])
@login_required
def update_password():
    user = User.query.get(session["user_id"])
    data = request.get_json() or {}
    current_pass = data.get("current_password", "")
    new_pass = data.get("new_password", "")
    confirm_pass = data.get("confirm_password", "")

    if not user.check_password(current_pass):
        return jsonify({"error": "Incorrect current password."}), 400
    if len(new_pass) < 6:
        return jsonify({"error": "New password must be at least 6 characters long."}), 400
    if new_pass != confirm_pass:
        return jsonify({"error": "New passwords do not match."}), 400

    user.set_password(new_pass)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Password updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update password: {str(e)}"}), 500

@settings_bp.route("/api/settings/seed-demo", methods=["POST"])
@login_required
def trigger_seed_demo():
    """Seeds rich demo data into the current logged-in user account."""
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "User not found."}), 404

    try:
        # Re-seed demo data for this user's email
        seed_demo_data(target_email=user.email, target_password="demo_retained_password")
        return jsonify({"success": True, "message": "Demo data populated successfully! Refresh dashboard to see all charts."})
    except Exception as e:
        return jsonify({"error": f"Failed to populate demo data: {str(e)}"}), 500

@settings_bp.route("/api/settings/clear-data", methods=["POST"])
@login_required
def clear_all_financial_data():
    """Wipes all financial transactions, budgets, goals, and reports for fresh manual entry."""
    user_id = session["user_id"]
    try:
        Income.query.filter_by(user_id=user_id).delete()
        Expense.query.filter_by(user_id=user_id).delete()
        Budget.query.filter_by(user_id=user_id).delete()
        SavingsGoal.query.filter_by(user_id=user_id).delete()
        FinancialReport.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({"success": True, "message": "All financial records cleared successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to clear data: {str(e)}"}), 500
