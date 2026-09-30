from datetime import datetime, date
from . import db

class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    target_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def remaining_amount(self) -> float:
        rem = self.target_amount - self.current_amount
        return max(0.0, round(rem, 2))

    @property
    def progress_percentage(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, round((self.current_amount / self.target_amount) * 100, 1))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "target_amount": round(self.target_amount, 2),
            "current_amount": round(self.current_amount, 2),
            "remaining_amount": self.remaining_amount,
            "progress_percentage": self.progress_percentage,
            "target_date": self.target_date.strftime("%Y-%m-%d") if self.target_date else None,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<SavingsGoal {self.name} - ₹{self.current_amount}/₹{self.target_amount}>"
