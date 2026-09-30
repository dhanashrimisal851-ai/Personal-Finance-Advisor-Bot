from datetime import date, timedelta
from flask import Blueprint, render_template, request, jsonify, session
from sqlalchemy import extract, func
from models import db, Expense, Income
from routes.auth import login_required
from utils.validators import validate_positive_number, parse_date

expenses_bp = Blueprint("expenses", __name__)

@expenses_bp.route("/expenses")
@login_required
def expenses_view():
    return render_template("expenses.html")

@expenses_bp.route("/transactions")
@login_required
def transactions_view():
    return render_template("transactions.html")

@expenses_bp.route("/api/expenses", methods=["GET"])
@login_required
def get_expenses():
    user_id = session["user_id"]
    category = request.args.get("category")
    payment_method = request.args.get("payment_method")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sort_by", "date_desc")
    view_mode = request.args.get("view_mode")  # 'weekly', 'monthly', or None

    query = Expense.query.filter_by(user_id=user_id)

    today = date.today()
    if view_mode == "weekly":
        start_of_week = today - timedelta(days=today.weekday())
        query = query.filter(Expense.date >= start_of_week)
    elif view_mode == "monthly":
        query = query.filter(
            extract("month", Expense.date) == today.month,
            extract("year", Expense.date) == today.year
        )

    if category and category != "All":
        query = query.filter(Expense.category == category)
    if payment_method and payment_method != "All":
        query = query.filter(Expense.payment_method == payment_method)
    if start_date:
        s_dt = parse_date(start_date)
        if s_dt:
            query = query.filter(Expense.date >= s_dt)
    if end_date:
        e_dt = parse_date(end_date)
        if e_dt:
            query = query.filter(Expense.date <= e_dt)
    if search:
        query = query.filter(
            (Expense.description.ilike(f"%{search}%")) |
            (Expense.category.ilike(f"%{search}%"))
        )

    if sort_by == "amount_desc":
        query = query.order_by(Expense.amount.desc())
    elif sort_by == "amount_asc":
        query = query.order_by(Expense.amount.asc())
    elif sort_by == "date_asc":
        query = query.order_by(Expense.date.asc(), Expense.id.asc())
    else:
        query = query.order_by(Expense.date.desc(), Expense.id.desc())

    expenses = query.all()
    total_amount = sum(e.amount for e in expenses)

    return jsonify({
        "success": True,
        "expenses": [e.to_dict() for e in expenses],
        "total_amount": round(total_amount, 2),
        "valid_categories": Expense.VALID_CATEGORIES,
        "valid_payment_methods": Expense.VALID_PAYMENT_METHODS
    })

@expenses_bp.route("/api/expenses", methods=["POST"])
@login_required
def add_expense():
    user_id = session["user_id"]
    data = request.get_json() or {}

    valid_amt, amount = validate_positive_number(data.get("amount"))
    if not valid_amt:
        return jsonify({"error": "Please enter a valid positive amount."}), 400

    category = (data.get("category") or "").strip()
    if category not in Expense.VALID_CATEGORIES:
        return jsonify({"error": f"Invalid category. Choose from: {', '.join(Expense.VALID_CATEGORIES)}"}), 400

    payment_method = (data.get("payment_method") or "UPI").strip()
    dt = parse_date(data.get("date")) or date.today()
    description = (data.get("description") or "").strip()

    try:
        new_expense = Expense(
            user_id=user_id,
            amount=amount,
            category=category,
            date=dt,
            description=description,
            payment_method=payment_method
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({"success": True, "message": "Expense recorded successfully!", "expense": new_expense.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to record expense: {str(e)}"}), 500

@expenses_bp.route("/api/expenses/<int:expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id):
    user_id = session["user_id"]
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return jsonify({"error": "Expense record not found."}), 404

    data = request.get_json() or {}

    if "amount" in data:
        valid_amt, amount = validate_positive_number(data["amount"])
        if not valid_amt:
            return jsonify({"error": "Amount must be a positive number."}), 400
        expense.amount = amount

    if "category" in data:
        cat = data["category"].strip()
        if cat not in Expense.VALID_CATEGORIES:
            return jsonify({"error": "Invalid category."}), 400
        expense.category = cat

    if "payment_method" in data:
        expense.payment_method = (data["payment_method"] or "UPI").strip()

    if "date" in data:
        dt = parse_date(data["date"])
        if dt:
            expense.date = dt

    if "description" in data:
        expense.description = (data["description"] or "").strip()

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Expense updated successfully!", "expense": expense.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500

@expenses_bp.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    user_id = session["user_id"]
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return jsonify({"error": "Expense record not found."}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"success": True, "message": "Expense deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500

@expenses_bp.route("/api/transactions", methods=["GET"])
@login_required
def get_all_transactions():
    """Unified transactions list for Income and Expense records with filtering, searching, and sorting."""
    user_id = session["user_id"]
    tx_type = request.args.get("type", "All")  # All, Income, Expense
    search = request.args.get("search", "").strip().lower()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    items = []

    # Get incomes
    if tx_type in ("All", "Income"):
        inc_q = Income.query.filter_by(user_id=user_id)
        if start_date and parse_date(start_date):
            inc_q = inc_q.filter(Income.date >= parse_date(start_date))
        if end_date and parse_date(end_date):
            inc_q = inc_q.filter(Income.date <= parse_date(end_date))
        for inc in inc_q.all():
            if search and search not in inc.source.lower() and search not in (inc.description or "").lower():
                continue
            items.append({
                "id": inc.id,
                "type": "Income",
                "category_source": inc.source,
                "description": inc.description or "",
                "amount": inc.amount,
                "date": inc.date.strftime("%Y-%m-%d"),
                "payment_method": "Bank"
            })

    # Get expenses
    if tx_type in ("All", "Expense"):
        exp_q = Expense.query.filter_by(user_id=user_id)
        if start_date and parse_date(start_date):
            exp_q = exp_q.filter(Expense.date >= parse_date(start_date))
        if end_date and parse_date(end_date):
            exp_q = exp_q.filter(Expense.date <= parse_date(end_date))
        for exp in exp_q.all():
            if search and search not in exp.category.lower() and search not in (exp.description or "").lower():
                continue
            items.append({
                "id": exp.id,
                "type": "Expense",
                "category_source": exp.category,
                "description": exp.description or "",
                "amount": exp.amount,
                "date": exp.date.strftime("%Y-%m-%d"),
                "payment_method": exp.payment_method
            })

    # Sort items by date desc, then amount desc
    items.sort(key=lambda x: (x["date"], x["amount"]), reverse=True)

    return jsonify({
        "success": True,
        "transactions": items,
        "count": len(items)
    })
