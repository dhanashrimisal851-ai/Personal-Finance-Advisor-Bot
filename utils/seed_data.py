from datetime import date, timedelta
from models import db, User, Income, Expense, Budget, SavingsGoal, FinancialReport

def seed_demo_data(target_email="demo@example.com", target_password="demo123"):
    """Seeds the database with realistic demo financial data for demonstration."""
    user = User.query.filter_by(email=target_email).first()
    
    if not user:
        user = User(
            name="Demo User",
            email=target_email
        )
        user.set_password(target_password)
        db.session.add(user)
        db.session.commit()
    else:
        # Clear existing financial records for this demo user to cleanly re-seed
        Income.query.filter_by(user_id=user.id).delete()
        Expense.query.filter_by(user_id=user.id).delete()
        Budget.query.filter_by(user_id=user.id).delete()
        SavingsGoal.query.filter_by(user_id=user.id).delete()
        FinancialReport.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # 1. Income: ₹30,000 (Salary)
    salary_income = Income(
        user_id=user.id,
        amount=30000.0,
        source="Salary",
        date=date(current_year, current_month, 1),
        description="Monthly Professional Salary"
    )
    db.session.add(salary_income)

    # 2. Expenses (totaling ₹19,500 so Savings = ₹10,500 as requested)
    # Rent: ₹8,000, Food: ₹4,500, Transport: ₹2,000, Entertainment: ₹1,500, Shopping: ₹2,000, Utilities: ₹1,500
    sample_expenses = [
        {"cat": "Rent", "amt": 8000.0, "day": 2, "desc": "Apartment monthly rent", "method": "Net Banking"},
        {"cat": "Food", "amt": 2200.0, "day": 5, "desc": "Monthly grocery restocking", "method": "Debit Card"},
        {"cat": "Food", "amt": 1300.0, "day": 12, "desc": "Weekend dining & takeout", "method": "UPI"},
        {"cat": "Food", "amt": 1000.0, "day": 20, "desc": "Fresh fruits & daily supplies", "method": "UPI"},
        {"cat": "Transport", "amt": 1200.0, "day": 7, "desc": "Monthly metro pass & fuel", "method": "UPI"},
        {"cat": "Transport", "amt": 800.0, "day": 18, "desc": "Cab ride for airport transit", "method": "UPI"},
        {"cat": "Entertainment", "amt": 800.0, "day": 9, "desc": "Movie tickets with friends", "method": "Credit Card"},
        {"cat": "Entertainment", "amt": 700.0, "day": 15, "desc": "Streaming subscriptions (OTT)", "method": "Credit Card"},
        {"cat": "Shopping", "amt": 2000.0, "day": 14, "desc": "Seasonal clothing & essentials", "method": "Credit Card"},
        {"cat": "Bills & Utilities", "amt": 1500.0, "day": 10, "desc": "Electricity and high-speed Wi-Fi", "method": "Net Banking"}
    ]

    for item in sample_expenses:
        exp_date = date(current_year, current_month, min(item["day"], 28))
        exp = Expense(
            user_id=user.id,
            amount=item["amt"],
            category=item["cat"],
            date=exp_date,
            description=item["desc"],
            payment_method=item["method"]
        )
        db.session.add(exp)

    # 3. Monthly Budgets
    sample_budgets = [
        {"cat": "Rent", "amt": 8000.0},
        {"cat": "Food", "amt": 5000.0},              # Spent 4500 (90%) - warning / alert boundary
        {"cat": "Transport", "amt": 2500.0},         # Spent 2000 (80%)
        {"cat": "Shopping", "amt": 2500.0},          # Spent 2000 (80%)
        {"cat": "Entertainment", "amt": 1500.0},     # Spent 1500 (100%) - overspending alert!
        {"cat": "Bills & Utilities", "amt": 2000.0}, # Spent 1500 (75%)
        {"cat": "Healthcare", "amt": 1000.0},
    ]

    for b in sample_budgets:
        budget = Budget(
            user_id=user.id,
            category=b["cat"],
            amount=b["amt"],
            month=current_month,
            year=current_year
        )
        db.session.add(budget)

    # 4. Savings Goal: "New Laptop", Target: ₹60,000, Saved: ₹25,000
    target_dt = today + timedelta(days=90)
    goal = SavingsGoal(
        user_id=user.id,
        name="New Laptop",
        target_amount=60000.0,
        current_amount=25000.0,
        target_date=target_dt,
        description="High-performance work & creative laptop"
    )
    db.session.add(goal)

    # Secondary goal for demonstration: "Emergency Fund"
    goal2 = SavingsGoal(
        user_id=user.id,
        name="Emergency Fund",
        target_amount=50000.0,
        current_amount=35000.0,
        target_date=today + timedelta(days=120),
        description="3 months living reserve in liquid savings"
    )
    db.session.add(goal2)

    # 5. Prior Month's Data (for comparative analytics: current vs previous month)
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1

    prev_salary = Income(
        user_id=user.id,
        amount=30000.0,
        source="Salary",
        date=date(prev_year, prev_month, 1),
        description="Previous Month Salary"
    )
    db.session.add(prev_salary)

    prev_expenses = [
        {"cat": "Rent", "amt": 8000.0, "day": 2, "desc": "Apartment rent"},
        {"cat": "Food", "amt": 5200.0, "day": 10, "desc": "Food & dining"},
        {"cat": "Transport", "amt": 2200.0, "day": 14, "desc": "Commute travel"},
        {"cat": "Entertainment", "amt": 2200.0, "day": 18, "desc": "Concerts & gaming"},
        {"cat": "Shopping", "amt": 3500.0, "day": 22, "desc": "Online shopping"},
        {"cat": "Bills & Utilities", "amt": 1600.0, "day": 8, "desc": "Bills"}
    ]
    for p in prev_expenses:
        exp = Expense(
            user_id=user.id,
            amount=p["amt"],
            category=p["cat"],
            date=date(prev_year, prev_month, min(p["day"], 28)),
            description=p["desc"],
            payment_method="UPI"
        )
        db.session.add(exp)

    db.session.commit()
    return user
