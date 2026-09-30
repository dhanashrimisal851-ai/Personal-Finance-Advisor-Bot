from datetime import datetime
from . import db

class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)   # 1 - 12
    year = db.Column(db.Integer, nullable=False)    # e.g. 2026
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint per user, category, month, year
    __table_args__ = (
        db.UniqueConstraint("user_id", "category", "month", "year", name="uq_user_cat_month_year"),
    )

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

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "amount": round(self.amount, 2),
            "month": self.month,
            "year": self.year,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Budget {self.category} ({self.month}/{self.year}) - ₹{self.amount}>"
