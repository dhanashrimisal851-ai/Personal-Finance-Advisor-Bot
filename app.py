import os
import sys
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from config import Config
from models import db, User
from routes import (
    auth_bp,
    dashboard_bp,
    income_bp,
    expenses_bp,
    budget_bp,
    goals_bp,
    analytics_bp,
    ai_bp,
    reports_bp,
    settings_bp
)
from utils.seed_data import seed_demo_data

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Landing page route
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard.dashboard_view"))
        return render_template("index.html")

    # Global template context processor
    @app.context_processor
    def inject_user():
        current_user = None
        if "user_id" in session:
            current_user = {
                "id": session["user_id"],
                "name": session.get("user_name", "User"),
                "email": session.get("user_email", "")
            }
        return dict(current_user=current_user)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("index.html", error_message="The requested page was not found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("index.html", error_message="An internal server error occurred. Please try again."), 500

    # Ensure tables exist and seed demo account if needed
    with app.app_context():
        db.create_all()
        # Create Demo User if not present
        if not User.query.filter_by(email="demo@example.com").first():
            try:
                seed_demo_data()
                print(">> Demo user seeded successfully: demo@example.com / demo123")
            except Exception as ex:
                print(f"Notice: Demo data initialization skipped: {ex}")

    return app

app = create_app()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        with app.app_context():
            seed_demo_data()
            print(">> Demo database freshly seeded with sample data.")
    else:
        port = int(os.getenv("PORT", 5050))
        print(f"================================================================")
        print(f"  PERSONAL FINANCE ADVISOR BOT")
        print(f"  Tagline: 'Track. Understand. Save. Grow.'")
        print(f"  Running at: http://127.0.0.1:{port}")
        print(f"  Demo Login: demo@example.com / demo123")
        print(f"================================================================")
        app.run(host="0.0.0.0", port=port, debug=True)
