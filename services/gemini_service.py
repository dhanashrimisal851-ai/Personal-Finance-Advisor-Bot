import os
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

# System instructions
SYSTEM_PROMPT = """You are a supportive, knowledgeable personal budgeting assistant and financial educator.
Analyze the user's financial details and provide clear, practical, and actionable budgeting recommendations.
Always format currency in Indian Rupees (₹).
Do not claim to be a certified financial advisor or legal professional.
Do not promise or guarantee investment or financial returns.
Keep responses concise, clear, and structured with:
- AI Insight: Quick overarching observation
- Problem Identified: Primary friction or risk area in the user's spending/saving pattern
- Recommendation: Core strategic advice
- Action Steps: 3-4 concrete bullet points the user can do immediately.
"""

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or Config.GEMINI_API_KEY
    if not api_key or api_key.strip() == "" or api_key.startswith("your_"):
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key.strip())
        # Try gemini-1.5-flash or gemini-2.5-flash
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini client: {e}")
        return None

def generate_ai_budget_plan(income: float, fixed_expenses: float, variable_expenses: float, goal: str, savings_pct: float):
    """
    Generates a personalized budget plan (Needs, Wants, Savings, Emergency Fund)
    with reasons and educational guidance.
    """
    income = max(0.0, float(income))
    desired_savings_pct = max(0.0, min(80.0, float(savings_pct or 20.0)))
    
    # Calculate targets
    target_savings = round((income * desired_savings_pct) / 100.0, 2)
    emergency_fund = round(target_savings * 0.3, 2)
    direct_savings = round(target_savings * 0.7, 2)
    
    # 50/30/20 baseline adjusted for user input
    available_for_spending = max(0.0, income - target_savings)
    needs = round(min(available_for_spending * 0.7, fixed_expenses if fixed_expenses > 0 else available_for_spending * 0.6), 2)
    wants = round(max(0.0, available_for_spending - needs), 2)

    prompt = f"""
{SYSTEM_PROMPT}

A user is asking for a personalized budget plan:
- Monthly Income: ₹{income:,.2f}
- Fixed Expenses: ₹{fixed_expenses:,.2f}
- Variable Expenses: ₹{variable_expenses:,.2f}
- Financial Goal: {goal or 'Financial Stability'}
- Desired Savings Percentage: {desired_savings_pct}%

Please produce a structured JSON response with exactly these keys:
{{
  "needs": {needs},
  "wants": {wants},
  "savings": {direct_savings},
  "emergency_fund": {emergency_fund},
  "explanation": "Detailed explanation of why this budget split works for their specific goal and income",
  "category_allocations": [
    {{"category": "Rent", "amount": 0, "tip": "..."}},
    {{"category": "Food", "amount": 0, "tip": "..."}},
    {{"category": "Transport", "amount": 0, "tip": "..."}},
    {{"category": "Bills & Utilities", "amount": 0, "tip": "..."}},
    {{"category": "Shopping", "amount": 0, "tip": "..."}},
    {{"category": "Entertainment", "amount": 0, "tip": "..."}},
    {{"category": "Healthcare", "amount": 0, "tip": "..."}},
    {{"category": "Other", "amount": 0, "tip": "..."}}
  ],
  "action_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}
Return ONLY valid JSON.
"""

    model = get_gemini_client()
    if model:
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            parsed = json.loads(text.strip())
            parsed["source"] = "Gemini AI"
            return parsed
        except Exception as e:
            logger.error(f"Gemini API generation error: {e}")

    # Fallback intelligent rule-based generator
    rent_alloc = round(needs * 0.55, 2)
    food_alloc = round(needs * 0.30, 2)
    utilities_alloc = round(needs * 0.15, 2)
    transport_alloc = round(wants * 0.35, 2)
    shopping_alloc = round(wants * 0.35, 2)
    entertainment_alloc = round(wants * 0.30, 2)

    return {
        "source": "Smart Financial Advisor Engine",
        "needs": needs,
        "wants": wants,
        "savings": direct_savings,
        "emergency_fund": emergency_fund,
        "explanation": (
            f"Based on your ₹{income:,.0f} income and goal of '{goal or 'Healthy Savings'}', "
            f"we tailored a balanced plan: ₹{needs:,.0f} for essentials ({round((needs/income)*100 if income else 0)}%), "
            f"₹{wants:,.0f} for discretionary spending ({round((wants/income)*100 if income else 0)}%), and "
            f"₹{target_savings:,.0f} ({desired_savings_pct}%) dedicated to savings & emergency fund buffer. "
            "This shields you from sudden expenses while steadily advancing your target."
        ),
        "category_allocations": [
            {"category": "Rent", "amount": rent_alloc, "tip": "Keep fixed housing costs below 30% of income."},
            {"category": "Food", "amount": food_alloc, "tip": "Meal plan weekly to prevent grocery waste and dining spikes."},
            {"category": "Transport", "amount": transport_alloc, "tip": "Use transit passes or shared rides for regular commutes."},
            {"category": "Bills & Utilities", "amount": utilities_alloc, "tip": "Audit monthly subscriptions and power consumption."},
            {"category": "Shopping", "amount": shopping_alloc, "tip": "Follow a 48-hour cooling-off rule on non-essential purchases."},
            {"category": "Entertainment", "amount": entertainment_alloc, "tip": "Enjoy leisure guilt-free within this preset cap."},
            {"category": "Healthcare", "amount": round(income * 0.05, 2), "tip": "Keep a regular health & medical buffer."},
            {"category": "Other", "amount": round(income * 0.03, 2), "tip": "Unforeseen miscellaneous expenses buffer."}
        ],
        "action_tips": [
            f"Automate transfer of ₹{direct_savings:,.0f} directly to your savings on payday.",
            "Use UPI limits or a separate debit card for discretionary entertainment & dining.",
            "Track weekly rather than waiting for month-end to spot overspending early."
        ]
    }

def get_ai_financial_advice(question: str, context: dict):
    """
    Answers user queries with tailored financial insights, problem identification,
    recommendations, and action steps using user's real financial context.
    """
    income = context.get("total_income", 0.0)
    expenses = context.get("total_expense", 0.0)
    savings = context.get("total_savings", 0.0)
    savings_rate = context.get("savings_rate", 0.0)
    top_categories = context.get("top_categories", [])
    overspent_categories = context.get("overspent_categories", [])
    goals = context.get("goals", [])

    top_cat_summary = ", ".join([f"{c['category']}: ₹{c['amount']:,.0f} ({c['percentage']}%)" for c in top_categories[:3]]) or "None recorded"
    overspent_summary = ", ".join(overspent_categories) if overspent_categories else "None (All within budget limits)"
    goals_summary = ", ".join([f"{g['name']} (₹{g['current_amount']:,.0f} / ₹{g['target_amount']:,.0f})" for g in goals]) or "No active goals"

    context_str = f"""
Current User Monthly Financial Snapshot:
- Monthly Income: ₹{income:,.2f}
- Monthly Expenses: ₹{expenses:,.2f}
- Current Monthly Savings: ₹{savings:,.2f} (Savings Rate: {savings_rate}%)
- Top Spending Categories: {top_cat_summary}
- Overspent Budget Categories: {overspent_summary}
- Active Savings Goals: {goals_summary}
"""

    prompt = f"""
{SYSTEM_PROMPT}

{context_str}

User Question: "{question}"

Please provide your response strictly in the following JSON format:
{{
  "insight": "1-2 sentence high-level observation directly relating their data to their question.",
  "problem": "Clear identification of the friction point, risk, or habit hindering their progress.",
  "recommendation": "Strategic guidance and advice tailored to this user's numbers.",
  "action_steps": [
    "Step 1: Specific action with amounts where applicable",
    "Step 2: Concrete operational adjustment",
    "Step 3: Forward-looking milestone or habit"
  ]
}}
Return ONLY valid JSON.
"""

    model = get_gemini_client()
    if model:
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            parsed = json.loads(text.strip())
            parsed["source"] = "Gemini AI"
            return parsed
        except Exception as e:
            logger.error(f"Gemini API error in advice generation: {e}")

    # Fallback intelligent rule-based heuristic advisor
    q_lower = question.lower()
    
    # 1. Reduce monthly expenses / where am I overspending
    if "reduce" in q_lower or "overspending" in q_lower or "cut" in q_lower:
        top_cat = top_categories[0]["category"] if top_categories else "Dining & Discretionary"
        top_amt = top_categories[0]["amount"] if top_categories else expenses * 0.3
        
        insight = f"Your highest expense category is currently {top_cat} at ₹{top_amt:,.0f}."
        problem = (
            f"You have overspent in: {overspent_summary}." if overspent_categories
            else f"Your total expenses of ₹{expenses:,.0f} consume {round((expenses/income)*100 if income else 0)}% of your monthly cash flow."
        )
        recommendation = f"Target reducing non-essential expenses in {top_cat} by 15-20% to free up at least ₹{round(top_amt * 0.15):,.0f} each month."
        action_steps = [
            f"Audit every transaction in '{top_cat}' from the last 30 days and flag recurring or impulse charges.",
            "Establish a strict weekly cap instead of a monthly allowance so overspending is detected by Sunday.",
            "Switch to cash or a zero-balance prepaid account specifically for dining and leisure to cap outflows automatically."
        ]

    # 2. How much should I save / plan to save
    elif "save" in q_lower or "saving" in q_lower or "50,000" in q_lower:
        target_savings_amt = income * 0.25 if income > 0 else 5000.0
        insight = f"You are currently saving ₹{savings:,.0f} per month ({savings_rate:.1f}% savings rate)."
        problem = "Inconsistent monthly contributions and variable discretionary spending make it difficult to hit milestone savings targets."
        recommendation = f"Adopt a 'Pay Yourself First' rule: route ₹{target_savings_amt:,.0f} (20-30% of income) into a designated savings vehicle before paying any discretionary bills."
        action_steps = [
            f"Schedule an automatic recurring transfer of ₹{round(target_savings_amt):,.0f} on the 1st of every month.",
            f"Allocate this toward your active goals ({goals_summary}).",
            "Any bonus or freelance income should adhere to a 70/30 rule: 70% to savings, 30% for guilt-free spend."
        ]

    # 3. Emergency fund
    elif "emergency" in q_lower or "fund" in q_lower:
        target_emergency = expenses * 3 if expenses > 0 else 45000.0
        insight = f"A solid emergency fund for your spending level should be at least 3 months of expenses: ₹{target_emergency:,.0f}."
        problem = "Without a ring-fenced emergency liquid reserve, any medical or vehicle mishap forces debt or liquidation of long-term assets."
        recommendation = f"Build an emergency fund of ₹{target_emergency:,.0f} stored in a high-yield liquid savings account or flexi-FD with instant withdrawal access."
        action_steps = [
            f"Start with a mini-target of ₹{round(target_emergency / 3):,.0f} within 60 days.",
            "Park the funds in a separate bank account with no UPI or debit card linked for daily spending.",
            "Treat unexpected expenses as loans from yourself that must be replenished the following month."
        ]

    # 4. Allowance / student / starter budget
    elif "allowance" in q_lower or "15,000" in q_lower or "student" in q_lower:
        insight = "Managing a modest monthly allowance requires strict boundary rules between needs and social spending."
        problem = "Social dining, convenience transport, and digital micro-transactions rapidly deplete lump-sum allowances in the first 10 days."
        recommendation = "Divide your ₹15,000 into weekly envelopes: ₹3,750 per week max, reserving ₹1,500 at the start of the month as an emergency safety net."
        action_steps = [
            "Withdraw or transfer your weekly spending budget every Monday morning.",
            "Cook or prep shared meals with friends instead of delivery apps to cut food costs in half.",
            "Track daily expenses on this app each evening to keep your running balance visible."
        ]

    # 5. Expenses increasing / why are my expenses rising
    elif "increasing" in q_lower or "rising" in q_lower or "why" in q_lower:
        insight = f"Your recorded monthly expenses stand at ₹{expenses:,.0f} with {len(overspent_categories)} categories triggering budget warnings."
        problem = "Lifestyle creep, small unchecked digital payments, and subtle inflation across food and transit frequently cause expenses to creep up unnoticed."
        recommendation = "Run a zero-based budget audit for 14 days, verifying every subscription, automated debit, and convenience purchase."
        action_steps = [
            "Cancel any OTT, gym, or software subscription unused in the last 30 days.",
            "Check for delivery surge fees and delivery app markup prices.",
            "Set push notifications on your bank accounts for all debits greater than ₹500."
        ]

    # General fallback
    else:
        insight = f"Based on your ₹{income:,.0f} income and ₹{expenses:,.0f} expenses, your current financial surplus is ₹{savings:,.0f}."
        problem = "Lack of automated financial boundaries often leads to cash leakage and missed savings milestones."
        recommendation = "Focus on the 50/30/20 framework: 50% for Needs, 30% for Wants, and at least 20% guaranteed toward Savings & Debt Freedom."
        action_steps = [
            "Review your category budgets on the Budget page and ensure no category exceeds 90% usage.",
            "Review your top spending areas and set a personal savings milestone for this quarter.",
            "Re-visit this AI advisor anytime you consider a major financial decision or purchase."
        ]

    return {
        "source": "Smart Financial Advisor Engine",
        "insight": insight,
        "problem": problem,
        "recommendation": recommendation,
        "action_steps": action_steps
    }
