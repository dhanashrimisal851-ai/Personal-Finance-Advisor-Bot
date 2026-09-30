from datetime import datetime, date
from . import db

class Income(db.Model):
    __tablename__ = "incomes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    VALID_SOURCES = [
        "Salary",
        "Freelancing",
        "Allowance",
        "Business",
        "Investment",
        "Other"
    ]

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": round(self.amount, 2),
            "source": self.source,
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Income {self.source} - ₹{self.amount}>"
