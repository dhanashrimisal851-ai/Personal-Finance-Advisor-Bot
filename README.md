# PERSONAL FINANCE ADVISOR BOT
> **Tagline:** *“Track. Understand. Save. Grow.”*

An AI-powered personal finance management and wealth-building platform built with Python (Flask), SQLite, SQLAlchemy, Chart.js, ReportLab, and Google Gemini AI.

---

## 📌 Project Overview & Problem Statement

### The Problem
Millions of individuals struggle with day-to-day cash flow management:
- They spend without clear visibility into where their money goes.
- Budgets are difficult to calculate and maintain manually.
- They fall into the paycheck-to-paycheck trap due to unseen discretionary leaks.
- Generic financial apps only show raw transaction tables without explainable advice.

### The Solution
**Personal Finance Advisor Bot** bridges the gap between tracking and actionable behavioral transformation:
1. **Real-time Cash Flow Monitoring:** Track income inflows and daily expenses categorized with payment methods (UPI, Cards, Net Banking, Cash).
2. **Proactive Budget Adherence:** Dynamic visual limits that issue warnings at 70% and overspending alerts at 90%.
3. **AI Smart Budget Generator:** Automatically computes a 50/30/20 balanced budget (Needs, Wants, Savings, Emergency Fund) based on monthly earnings and targets.
4. **Google Gemini AI Advisor:** Analyzes your actual spending data to diagnose problems, pinpoint leaks, and provide immediate step-by-step action plans.
5. **Milestone Savings Tracker & Calculator:** Set targets (e.g. Emergency Fund, Laptop) and compute exact monthly contributions required.
6. **Executive Monthly Reports:** Downloadable 2-page PDF statements powered by ReportLab, plus on-screen printable views.
7. **Transparent Financial Health Score (0–100):** Rule-based score evaluating savings rate, budget adherence, and goal momentum.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Authentication & Isolation** | Secure Werkzeug password hashing, session cookies, and strict per-user financial data isolation. |
| **Main Dashboard** | 5 core metrics (Income, Expenses, Savings, Savings Rate, Remaining Budget) in Indian Rupee (₹), health score, alerts, and recent transactions. |
| **Expense Management** | Add, edit, delete, search, sort, filter by category/date/payment method. Toggle between Weekly and Monthly views. |
| **Income Management** | Multi-income tracking across Salary, Freelancing, Allowance, Business, Investment, and Other. |
| **Unified Ledger** | Complete chronological audit trail with date filters, search, and instant delete capabilities. |
| **Smart Budget & AI Generator** | Custom category ceilings with color-coded progress bars (<70% normal, 70–90% warning, >90% alert) and 1-click AI plan applicator. |
| **Savings Goals & Calculator** | Visual progress tracking, deposit contributions, and a mathematical calculator for completion dates. |
| **Interactive Analytics** | Chart.js doughnut chart (category distribution), 6-month income vs. expense bar chart, savings line chart, and MoM category shifts. |
| **AI Financial Advisor** | Pre-built prompt chips or custom questions answered with structured AI Insight, Problem Identified, Recommendation, and Action Steps. |
| **Downloadable PDF Reports** | Professional monthly statements compiled on the fly using Python ReportLab. |
| **Demo Mode & Seed Data** | Pre-loaded with realistic demo data (₹30,000 salary, ₹19,500 expenses, ₹10,500 savings, Laptop goal) for instant evaluation. |

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, SQLite, Flask-CORS, Python-dotenv, Werkzeug
- **AI Integration:** Google Gemini API (`google-generativeai`) with resilient heuristic advisory fallback
- **Document Generation:** ReportLab 5.0 (vector PDF generation)
- **Frontend:** HTML5, CSS3 (Modern Dark + Blue FinTech design system), Vanilla JavaScript (ES6+)
- **Charts & Visualizations:** Chart.js 4.4
- **Typography & Icons:** Google Fonts (Outfit & Inter), Font Awesome 6

---

## 📂 Project Structure

```
Personal Finance Advisor Bot 3/
├── app.py                      # Flask factory, blueprint registration & boot logic
├── config.py                   # Central configuration & database URL resolution
├── requirements.txt            # Python dependencies
├── .env                        # Environment secrets (port, keys, secret key)
├── .env.example                # Example environment file template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation
│
├── models/                     # SQLAlchemy Database Models
│   ├── __init__.py             # Database instance export
│   ├── user.py                 # User authentication model
│   ├── income.py               # Income entry model
│   ├── expense.py              # Expense tracking model
│   ├── budget.py               # Category budget limits model
│   ├── savings_goal.py         # Savings milestone model
│   └── report.py               # Monthly financial statements model
│
├── routes/                     # Blueprint Modular Controllers
│   ├── __init__.py             # Blueprints bundle
│   ├── auth.py                 # Registration, login, logout, 1-click demo login
│   ├── dashboard.py            # Dashboard view & summary metrics API
│   ├── income.py               # Income CRUD & filtering APIs
│   ├── expenses.py             # Expense CRUD, filters & transaction view
│   ├── budget.py               # Budget CRUD & AI plan applicator
│   ├── goals.py                # Goals CRUD & savings calculator
│   ├── analytics.py            # Visualizations & MoM analytics API
│   ├── ai.py                   # Gemini AI financial advisor endpoints
│   ├── reports.py              # Monthly reports & PDF download endpoint
│   └── settings.py             # Profile, password, and demo data controls
│
├── services/                   # External Services
│   ├── __init__.py
│   └── gemini_service.py       # Google Gemini client & heuristic advisor engine
│
├── utils/                      # Helper Utilities
│   ├── __init__.py
│   ├── calculations.py         # Financial calculations & health score engine
│   ├── validators.py           # Sanitization & input validation
│   └── seed_data.py            # Realistic demo data populator
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Shared layout, sidebar & quick-action modals
│   ├── index.html              # Modern FinTech landing page
│   ├── login.html              # User login page
│   ├── register.html           # User registration page
│   ├── dashboard.html          # Main financial dashboard
│   ├── income.html             # Income management
│   ├── expenses.html           # Expense management
│   ├── transactions.html       # Unified ledger
│   ├── budget.html             # Budget adherence & AI planner
│   ├── goals.html              # Savings goals & calculator
│   ├── analytics.html          # Spending analytics & charts
│   ├── ai_advisor.html         # Interactive AI advisor page
│   ├── reports.html            # Monthly financial reports
│   └── settings.html           # User & system settings
│
├── static/                     # Static Assets
│   ├── css/
│   │   └── style.css           # Premium Dark Navy + Blue stylesheet
│   └── js/
│       ├── main.js             # Shared helpers, toasts, and quick modals
│       ├── dashboard.js        # Dashboard state & card population
│       ├── expenses.js         # Expense filtering & view mode switching
│       ├── income.js           # Income tracking & edits
│       ├── budget.js           # Budget progress & AI generator client
│       ├── goals.js            # Goals & calculator math
│       ├── analytics.js        # Chart.js initialization & comparison
│       ├── ai_advisor.js       # Interactive chat & structured cards
│       └── reports.js          # Statement renderer & PDF download
│
└── database/
    └── finance.db              # SQLite Database
```

---

## ⚙️ Installation & Setup

### 1. Clone or Open Project
Open the project directory in Visual Studio Code:
```bash
cd "Personal Finance Advisor Bot 3"
```

### 2. Create and Activate Virtual Environment
**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your keys:
```ini
SECRET_KEY=personal_finance_advisor_super_secret_key_2026
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5050
FLASK_ENV=development
FLASK_DEBUG=1
```
> **Note:** If you don't have a Gemini API key immediately, the platform automatically activates its **Smart Financial Advisor Engine** (intelligent heuristic fallback mode) so that every single AI feature, budget generator, and recommendation still works seamlessly!

---

## 🏃 Running the Application

Start the Flask development server:
```bash
python app.py
```

The application will initialize the SQLite database, seed the demo account if not already present, and launch at:
👉 **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

---

## 🧪 Demo Account Credentials

For quick evaluation, use the pre-seeded account:
- **Email:** `demo@example.com`
- **Password:** `demo123`
- *Or simply click **“1-Click Demo”** on the landing page or login screen!*

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/register` | `POST` | Create a new user account |
| `/api/login` | `POST` | Authenticate user & issue session |
| `/api/logout` | `POST` | Terminate active session |
| `/api/dashboard` | `GET` | Retrieve monthly finances, health score, alerts & goals |
| `/api/income` | `GET`, `POST` | List and add income records |
| `/api/income/<id>` | `PUT`, `DELETE` | Update or remove income entry |
| `/api/expenses` | `GET`, `POST` | List and add expense records |
| `/api/expenses/<id>` | `PUT`, `DELETE` | Update or remove expense entry |
| `/api/transactions` | `GET` | Unified income and expense chronological list |
| `/api/budget` | `GET`, `POST` | List and set category budget limits |
| `/api/budget/<id>` | `PUT`, `DELETE` | Update or delete budget ceiling |
| `/api/budget/apply-plan` | `POST` | Apply AI-generated category allocations |
| `/api/goals` | `GET`, `POST` | List and create savings goals |
| `/api/goals/<id>/contribute`| `POST` | Deposit funds towards an active goal |
| `/api/goals/calculator` | `POST` | Compute required savings and completion dates |
| `/api/analytics` | `GET` | Category distribution, 6-month trends & MoM comparison |
| `/api/ai/advice` | `POST` | Ask Gemini AI personal budgeting questions |
| `/api/ai/generate-budget` | `POST` | Generate 50/30/20 balanced budget allocations |
| `/api/report/<month>/<year>` | `GET` | Monthly financial report data |
| `/api/report/<month>/<year>/pdf` | `GET` | Generate and download ReportLab PDF statement |

---

## 🛡️ Security & Privacy
- Passwords hashed with `Werkzeug` PBKDF2:SHA256.
- Strict session cookie configuration (`HttpOnly`, `SameSite=Lax`).
- Clean per-user database partitioning: queries filter by `user_id = session['user_id']`.
- Never displays raw server stack traces to users.
- Disclaimers clearly communicate that AI advice is for financial literacy and personal budgeting education.
