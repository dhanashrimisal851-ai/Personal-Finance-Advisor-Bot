import io
from datetime import date
from flask import Blueprint, render_template, request, jsonify, session, send_file, make_response
from models import db, FinancialReport, User
from routes.auth import login_required
from utils.calculations import (
    get_monthly_finances,
    get_category_breakdown,
    get_budget_performance,
    calculate_financial_health_score
)
from services.gemini_service import get_ai_financial_advice

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/reports")
@login_required
def reports_view():
    return render_template("reports.html")

@reports_bp.route("/api/report/<int:month>/<int:year>", methods=["GET"])
@login_required
def get_report_data(month, year):
    user_id = session["user_id"]
    finances = get_monthly_finances(user_id, month, year)
    categories = get_category_breakdown(user_id, month, year)
    budget_perf = get_budget_performance(user_id, month, year)
    health = calculate_financial_health_score(user_id, month, year)

    # Context for AI recommendation in report
    context = {
        "total_income": finances["total_income"],
        "total_expense": finances["total_expense"],
        "total_savings": finances["total_savings"],
        "savings_rate": finances["savings_rate"],
        "top_categories": categories[:3],
        "overspent_categories": budget_perf["overspent_categories"],
        "goals": []
    }
    ai_advice = get_ai_financial_advice("Provide an executive monthly financial health summary and core recommendation.", context)

    # Save or update report in DB
    report_record = FinancialReport.query.filter_by(user_id=user_id, month=month, year=year).first()
    if not report_record:
        report_record = FinancialReport(
            user_id=user_id,
            month=month,
            year=year,
            total_income=finances["total_income"],
            total_expense=finances["total_expense"],
            total_savings=finances["total_savings"],
            savings_rate=finances["savings_rate"],
            ai_insights=ai_advice.get("recommendation", "")
        )
        report_record.set_category_summary(categories)
        db.session.add(report_record)
    else:
        report_record.total_income = finances["total_income"]
        report_record.total_expense = finances["total_expense"]
        report_record.total_savings = finances["total_savings"]
        report_record.savings_rate = finances["savings_rate"]
        report_record.ai_insights = ai_advice.get("recommendation", "")
        report_record.set_category_summary(categories)
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    return jsonify({
        "success": True,
        "month": month,
        "month_name": month_names[month] if 1 <= month <= 12 else str(month),
        "year": year,
        "finances": finances,
        "categories": categories,
        "budget_performance": budget_perf,
        "health_score": health,
        "ai_insights": ai_advice
    })

@reports_bp.route("/api/report/<int:month>/<int:year>/pdf", methods=["GET"])
@login_required
def download_pdf_report(month, year):
    """Generates and downloads a clean, printable PDF financial report."""
    user_id = session["user_id"]
    user = User.query.get(user_id)
    finances = get_monthly_finances(user_id, month, year)
    categories = get_category_breakdown(user_id, month, year)
    budget_perf = get_budget_performance(user_id, month, year)
    health = calculate_financial_health_score(user_id, month, year)

    month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_name = month_names[month] if 1 <= month <= 12 else str(month)

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )
        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155")
        )
        disclaimer_style = ParagraphStyle(
            "DocDisclaimer",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#94a3b8")
        )

        # Header Section
        story.append(Paragraph("PERSONAL FINANCE ADVISOR BOT", title_style))
        story.append(Paragraph(f"Monthly Financial Performance Report — <b>{month_name} {year}</b> | User: {user.name} ({user.email})", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=14))

        # Financial Summary Table (Cards)
        summary_data = [
            ["Monthly Income", "Total Expenses", "Net Savings", "Savings Rate", "Health Score"],
            [
                f"Rs. {finances['total_income']:,.0f}",
                f"Rs. {finances['total_expense']:,.0f}",
                f"Rs. {finances['total_savings']:,.0f}",
                f"{finances['savings_rate']:.1f}%",
                f"{health['score']}/100 ({health['badge']})"
            ]
        ]
        t_summary = Table(summary_data, colWidths=[108, 108, 108, 108, 108])
        t_summary.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#ffffff")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
            ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, 1), 11),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 14))

        # Category Breakdown Table
        story.append(Paragraph("Category Spending Breakdown", h2_style))
        if categories:
            cat_table_data = [["Category", "Amount Spent", "% of Total Expenses"]]
            for c in categories:
                cat_table_data.append([
                    c["category"],
                    f"Rs. {c['amount']:,.2f}",
                    f"{c['percentage']:.1f}%"
                ])
            cat_table_data.append([
                "Total Expenses",
                f"Rs. {finances['total_expense']:,.2f}",
                "100.0%"
            ])
            t_cat = Table(cat_table_data, colWidths=[200, 170, 170])
            t_cat.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#ffffff")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t_cat)
        else:
            story.append(Paragraph("No expenses recorded for this month.", body_style))

        story.append(Spacer(1, 14))

        # Budget Adherence Table
        story.append(Paragraph("Budget Performance", h2_style))
        if budget_perf["items"]:
            b_data = [["Category", "Budget Limit", "Spent", "Remaining", "Used %", "Status"]]
            for b in budget_perf["items"]:
                b_data.append([
                    b["category"],
                    f"Rs. {b['budget']:,.0f}",
                    f"Rs. {b['spent']:,.0f}",
                    f"Rs. {b['remaining']:,.0f}",
                    f"{b['percentage']:.1f}%",
                    b["status_text"]
                ])
            t_b = Table(b_data, colWidths=[130, 85, 85, 85, 65, 90])
            t_b.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("ALIGN", (1, 0), (4, -1), "RIGHT"),
                ("ALIGN", (5, 0), (5, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t_b)
        else:
            story.append(Paragraph("No category budgets were defined for this month.", body_style))

        story.append(Spacer(1, 14))

        # AI Insights Section
        story.append(Paragraph("AI Financial Health Assessment", h2_style))
        story.append(Paragraph(f"<b>Overview:</b> {health['summary']}", body_style))
        if health["positive_habits"]:
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Positive Observations:</b>", body_style))
            for habit in health["positive_habits"]:
                story.append(Paragraph(f"• {habit}", body_style))
        if health["areas_to_improve"]:
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Actionable Optimization Areas:</b>", body_style))
            for area in health["areas_to_improve"]:
                story.append(Paragraph(f"• {area}", body_style))

        story.append(Spacer(1, 18))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
        story.append(Paragraph("<b>Notice:</b> This automated statement is generated by Personal Finance Advisor Bot for personal budgeting and financial tracking purposes. It does not constitute certified legal, tax, or investment advice.", disclaimer_style))

        doc.build(story)
        buffer.seek(0)

        filename = f"Financial_Report_{month_name}_{year}.pdf"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500
