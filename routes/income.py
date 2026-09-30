from datetime import date
from flask import Blueprint, render_template, request, jsonify, session
from models import db, Income
from routes.auth import login_required
from utils.validators import validate_positive_number, parse_date

income_bp = Blueprint("income", __name__)

@income_bp.route("/income")
@login_required
def income_view():
    return render_template("income.html")

@income_bp.route("/api/income", methods=["GET"])
@login_required
def get_incomes():
    user_id = session["user_id"]
    source = request.args.get("source")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_by = request.args.get("sort_by", "date_desc")

    query = Income.query.filter_by(user_id=user_id)

    if source and source != "All":
        query = query.filter(Income.source == source)
    if start_date:
        s_dt = parse_date(start_date)
        if s_dt:
            query = query.filter(Income.date >= s_dt)
    if end_date:
        e_dt = parse_date(end_date)
        if e_dt:
            query = query.filter(Income.date <= e_dt)

    if sort_by == "amount_desc":
        query = query.order_by(Income.amount.desc())
    elif sort_by == "amount_asc":
        query = query.order_by(Income.amount.asc())
    elif sort_by == "date_asc":
        query = query.order_by(Income.date.asc(), Income.id.asc())
    else:
        query = query.order_by(Income.date.desc(), Income.id.desc())

    incomes = query.all()
    total_amount = sum(inc.amount for inc in incomes)

    return jsonify({
        "success": True,
        "incomes": [i.to_dict() for i in incomes],
        "total_amount": round(total_amount, 2),
        "valid_sources": Income.VALID_SOURCES
    })

@income_bp.route("/api/income", methods=["POST"])
@login_required
def add_income():
    user_id = session["user_id"]
    data = request.get_json() or {}

    valid_amt, amount = validate_positive_number(data.get("amount"))
    if not valid_amt:
        return jsonify({"error": "Please enter a valid positive amount."}), 400

    source = (data.get("source") or "").strip()
    if source not in Income.VALID_SOURCES:
        return jsonify({"error": f"Invalid source. Choose from: {', '.join(Income.VALID_SOURCES)}"}), 400

    dt = parse_date(data.get("date")) or date.today()
    description = (data.get("description") or "").strip()

    try:
        new_income = Income(
            user_id=user_id,
            amount=amount,
            source=source,
            date=dt,
            description=description
        )
        db.session.add(new_income)
        db.session.commit()
        return jsonify({"success": True, "message": "Income added successfully!", "income": new_income.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save income: {str(e)}"}), 500

@income_bp.route("/api/income/<int:income_id>", methods=["PUT"])
@login_required
def update_income(income_id):
    user_id = session["user_id"]
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()
    if not income:
        return jsonify({"error": "Income record not found."}), 404

    data = request.get_json() or {}

    if "amount" in data:
        valid_amt, amount = validate_positive_number(data["amount"])
        if not valid_amt:
            return jsonify({"error": "Amount must be a positive number."}), 400
        income.amount = amount

    if "source" in data:
        source = data["source"].strip()
        if source not in Income.VALID_SOURCES:
            return jsonify({"error": "Invalid income source."}), 400
        income.source = source

    if "date" in data:
        dt = parse_date(data["date"])
        if dt:
            income.date = dt

    if "description" in data:
        income.description = (data["description"] or "").strip()

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Income updated successfully!", "income": income.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update income: {str(e)}"}), 500

@income_bp.route("/api/income/<int:income_id>", methods=["DELETE"])
@login_required
def delete_income(income_id):
    user_id = session["user_id"]
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()
    if not income:
        return jsonify({"error": "Income record not found."}), 404

    try:
        db.session.delete(income)
        db.session.commit()
        return jsonify({"success": True, "message": "Income deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete income: {str(e)}"}), 500
