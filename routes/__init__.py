from .auth import auth_bp
from .dashboard import dashboard_bp
from .income import income_bp
from .expenses import expenses_bp
from .budget import budget_bp
from .goals import goals_bp
from .analytics import analytics_bp
from .ai import ai_bp
from .reports import reports_bp
from .settings import settings_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "income_bp",
    "expenses_bp",
    "budget_bp",
    "goals_bp",
    "analytics_bp",
    "ai_bp",
    "reports_bp",
    "settings_bp"
]
