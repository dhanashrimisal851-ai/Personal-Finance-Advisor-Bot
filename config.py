import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Ensure database directory exists
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "finance_advisor_default_secret_key_849204")
    db_url = os.getenv("DATABASE_URL")
    if not db_url or db_url.startswith("sqlite:///database"):
        db_file = (DB_DIR / "finance.db").resolve()
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file}"
    else:
        SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days
