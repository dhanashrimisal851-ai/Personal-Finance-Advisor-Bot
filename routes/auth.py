from functools import wraps
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from models import db, User
from utils.validators import validate_email
from utils.seed_data import seed_demo_data

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required. Please log in."}), 401
            return redirect(url_for("auth.login_view", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None

@auth_bp.route("/register", methods=["GET"])
def register_view():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard_view"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET"])
def login_view():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard_view"))
    return render_template("login.html")

@auth_bp.route("/demo-login", methods=["GET", "POST"])
def demo_login():
    """One-click login for demonstration with pre-seeded rich financial data."""
    user = User.query.filter_by(email="demo@example.com").first()
    if not user:
        user = seed_demo_data()
    
    session.clear()
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email
    session.permanent = True

    if request.is_json:
        return jsonify({"success": True, "message": "Logged in as Demo User", "user": user.to_dict()})
    return redirect(url_for("dashboard.dashboard_view"))

@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not name:
        return jsonify({"error": "Full Name is required."}), 400
    if not validate_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 400

    try:
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Log user in
        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email
        session.permanent = True

        return jsonify({"success": True, "message": "Registration successful!", "user": user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password. Please try again."}), 401

    session.clear()
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email
    session.permanent = True

    return jsonify({"success": True, "message": "Login successful!", "user": user.to_dict()})

@auth_bp.route("/logout", methods=["GET", "POST"])
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    if request.is_json or request.path.startswith("/api/"):
        return jsonify({"success": True, "message": "Logged out successfully."})
    return redirect(url_for("auth.login_view"))

@auth_bp.route("/api/me", methods=["GET"])
def get_me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 200
    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"authenticated": False}), 200
    return jsonify({"authenticated": True, "user": user.to_dict()})
