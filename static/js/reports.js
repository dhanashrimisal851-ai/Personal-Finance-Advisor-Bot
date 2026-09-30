// Monthly Reports JavaScript Logic

document.addEventListener("DOMContentLoaded", () => {
  const now = new Date();
  const mSelect = document.getElementById("reportMonth");
  const ySelect = document.getElementById("reportYear");
  if (mSelect) mSelect.value = String(now.getMonth() + 1);
  if (ySelect) ySelect.value = String(now.getFullYear());

  document.getElementById("reportGenDate").innerText = now.toLocaleDateString("en-IN", {
    day: "numeric", month: "long", year: "numeric"
  });

  loadReportData();
});

async function loadReportData() {
  const month = document.getElementById("reportMonth").value;
  const year = document.getElementById("reportYear").value;

  try {
    const res = await fetch(`/api/report/${month}/${year}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load report");

    document.getElementById("reportPeriodTitle").innerText = `${data.month_name} ${data.year} Statement`;
    
    // Numbers
    document.getElementById("repIncome").innerText = formatINR(data.finances.total_income);
    document.getElementById("repExpense").innerText = formatINR(data.finances.total_expense);
    document.getElementById("repSavings").innerText = formatINR(data.finances.total_savings);
    document.getElementById("repRate").innerText = `${data.finances.savings_rate}%`;

    // Category Table
    renderReportCategories(data.categories || []);

    // Budget Table
    renderReportBudgets(data.budget_performance || {});

    // AI Assessment
    renderReportAi(data.ai_insights || {}, data.health_score || {});

  } catch (err) {
    showToast(err.message, "danger");
  }
}

function renderReportCategories(categories) {
  const tbody = document.getElementById("reportCategoryTableBody");
  if (!tbody) return;

  if (categories.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="3" style="text-align: center; color: var(--text-muted); padding: 24px;">
          No expenses recorded for this reporting period.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  categories.forEach(c => {
    html += `
      <tr>
        <td><strong style="color: #fff;">${c.category}</strong></td>
        <td style="text-align: right; font-weight: 600; color: #fff;">${formatINR(c.amount)}</td>
        <td style="text-align: right; color: var(--text-muted);">${c.percentage}%</td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function renderReportBudgets(budgetPerf) {
  const tbody = document.getElementById("reportBudgetTableBody");
  if (!tbody) return;

  const items = budgetPerf.items || [];
  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 24px;">
          No category budgets were defined for this reporting period.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  items.forEach(b => {
    let badge = "badge-normal";
    if (b.status === "danger") badge = "badge-danger";
    else if (b.status === "warning") badge = "badge-warning";

    html += `
      <tr>
        <td><strong style="color: #fff;">${b.category}</strong></td>
        <td style="text-align: right;">${formatINR(b.budget)}</td>
        <td style="text-align: right; font-weight: 600; color: #fff;">${formatINR(b.spent)}</td>
        <td style="text-align: right; color: ${b.remaining < 0 ? '#f87171' : '#34d399'};">${formatINR(b.remaining)}</td>
        <td style="text-align: right;">${b.percentage}%</td>
        <td style="text-align: center;"><span class="badge ${badge}">${b.status_text}</span></td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function renderReportAi(ai, health) {
  const summaryEl = document.getElementById("reportAiSummary");
  const actionsList = document.getElementById("reportActionSteps");
  const actionsContainer = document.getElementById("reportActionStepsContainer");

  const recText = ai.recommendation || health.summary || "Consistent financial tracking maintained.";
  summaryEl.innerText = recText;

  if (ai.action_steps && ai.action_steps.length > 0) {
    actionsList.innerHTML = ai.action_steps.map(s => `<li>${s}</li>`).join("");
    actionsContainer.style.display = "block";
  } else {
    actionsContainer.style.display = "none";
  }
}

function downloadPdfReport() {
  const month = document.getElementById("reportMonth").value;
  const year = document.getElementById("reportYear").value;
  window.location.href = `/api/report/${month}/${year}/pdf`;
}
