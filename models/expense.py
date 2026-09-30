from datetime import datetime, date
from . import db

class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), default="UPI")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    VALID_CATEGORIES = [
        "Food",
        "Rent",
        "Transport",
        "Education",
        "Healthcare",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Travel",
        "Personal Care",
        "Other"
    ]

    VALID_PAYMENT_METHODS = [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Net Banking",
        "Cash",
        "Other"
    ]

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": round(self.amount, 2),
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "description": self.description or "",
            "payment_method": self.payment_method or "UPI",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Expense {self.category} - ₹{self.amount}>"
