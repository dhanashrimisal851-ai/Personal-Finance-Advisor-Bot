from datetime import datetime
import json
from . import db

class FinancialReport(db.Model):
    __tablename__ = "financial_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_income = db.Column(db.Float, default=0.0, nullable=False)
    total_expense = db.Column(db.Float, default=0.0, nullable=False)
    total_savings = db.Column(db.Float, default=0.0, nullable=False)
    savings_rate = db.Column(db.Float, default=0.0, nullable=False)
    category_summary_json = db.Column(db.Text, nullable=True)  # JSON string
    ai_insights = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "month", "year", name="uq_user_report_month_year"),
    )

    def get_category_summary(self):
        if self.category_summary_json:
            try:
                return json.loads(self.category_summary_json)
            except Exception:
                return {}
        return {}

    def set_category_summary(self, data_dict):
        self.category_summary_json = json.dumps(data_dict)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "month": self.month,
            "year": self.year,
            "total_income": round(self.total_income, 2),
            "total_expense": round(self.total_expense, 2),
            "total_savings": round(self.total_savings, 2),
            "savings_rate": round(self.savings_rate, 1),
            "category_summary": self.get_category_summary(),
            "ai_insights": self.ai_insights or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<FinancialReport {self.month}/{self.year} - ₹{self.total_income}/₹{self.total_expense}>"
