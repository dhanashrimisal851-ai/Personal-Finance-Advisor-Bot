// Budget Management JavaScript Logic

let currentBudgetPlan = null;

document.addEventListener("DOMContentLoaded", () => {
  const now = new Date();
  const mSelect = document.getElementById("budgetMonth");
  const ySelect = document.getElementById("budgetYear");
  if (mSelect) mSelect.value = String(now.getMonth() + 1);
  if (ySelect) ySelect.value = String(now.getFullYear());

  loadBudgets();
});

async function loadBudgets() {
  const month = document.getElementById("budgetMonth").value;
  const year = document.getElementById("budgetYear").value;

  try {
    const res = await fetch(`/api/budget?month=${month}&year=${year}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load budget data");

    const perf = data.performance;
    document.getElementById("budgetTotalDisplay").innerText = formatINR(perf.total_budgeted);
    document.getElementById("budgetCategoriesCount").innerText = `${perf.items.length} categories set`;
    document.getElementById("budgetSpentDisplay").innerText = formatINR(perf.total_spent_budgeted);
    document.getElementById("budgetRemainingDisplay").innerText = formatINR(perf.remaining_budget);
    document.getElementById("budgetOverspentCount").innerText = perf.overspent_count;

    renderBudgetGrid(perf.items || []);
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function renderBudgetGrid(items) {
  const grid = document.getElementById("budgetGrid");
  if (!grid) return;

  if (items.length === 0) {
    grid.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 48px; grid-column: 1 / -1;">
        <i class="fa-solid fa-sliders" style="font-size: 38px; color: var(--text-dim); margin-bottom: 14px; display: block;"></i>
        No budgets established for this month.<br>
        Click "Set Category Budget" or use the "AI Budget Generator" to get started instantly.
      </div>
    `;
    return;
  }

  let html = "";
  items.forEach(b => {
    let barColor = "normal";
    let badgeColor = "badge-normal";
    if (b.status === "danger") {
      barColor = "danger";
      badgeColor = "badge-danger";
    } else if (b.status === "warning") {
      barColor = "warning";
      badgeColor = "badge-warning";
    }

    const cappedPct = Math.min(b.percentage, 100);

    html += `
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; position: relative;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <div>
              <h3 style="font-size: 17px; font-weight: 700; color: #fff; margin-bottom: 2px;">${b.category}</h3>
              <span class="badge ${badgeColor}">${b.status_text} (${b.percentage}%)</span>
            </div>
            <div style="display: flex; gap: 4px;">
              <button class="btn btn-secondary btn-icon btn-sm" onclick="editBudgetInline('${b.category}', ${b.budget})" title="Edit Limit">
                <i class="fa-solid fa-pen"></i>
              </button>
              <button class="btn btn-danger btn-icon btn-sm" onclick="deleteBudget(${b.id})" title="Delete Budget">
                <i class="fa-solid fa-trash"></i>
              </button>
            </div>
          </div>

          <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">
              <span>Spent: <b style="color: #fff;">${formatINR(b.spent)}</b></span>
              <span>Limit: <b style="color: #fff;">${formatINR(b.budget)}</b></span>
            </div>
            <div class="progress" style="height: 10px;">
              <div class="progress-bar ${barColor}" style="width: ${cappedPct}%;"></div>
            </div>
          </div>
        </div>

        <div style="padding-top: 10px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; font-size: 12px; color: var(--text-dim);">
          <span>Remaining: <b style="color: ${b.remaining < 0 ? '#f87171' : '#34d399'}; font-size: 13px;">${formatINR(b.remaining)}</b></span>
          <span>${b.remaining < 0 ? 'Deficit' : 'Safe Margin'}</span>
        </div>
      </div>
    `;
  });

  grid.innerHTML = html;
}

function editBudgetInline(category, amount) {
  document.getElementById("budgetCategory").value = category;
  document.getElementById("budgetAmount").value = amount;
  openModal("setBudgetModal");
}

async function handleSetBudget(e) {
  e.preventDefault();
  const category = document.getElementById("budgetCategory").value;
  const amount = parseFloat(document.getElementById("budgetAmount").value);
  const month = document.getElementById("budgetMonth").value;
  const year = document.getElementById("budgetYear").value;

  try {
    const res = await fetch("/api/budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, amount, month, year })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to set budget");

    showToast(data.message, "success");
    closeModal("setBudgetModal");
    document.getElementById("setBudgetForm").reset();
    loadBudgets();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

async function deleteBudget(id) {
  if (!confirm("Are you sure you want to remove this budget limit?")) return;

  try {
    const res = await fetch(`/api/budget/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete budget");

    showToast("Budget limit removed.", "info");
    loadBudgets();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

// AI Budget Generator Logic
async function handleGenerateAiBudget(e) {
  e.preventDefault();
  const income = parseFloat(document.getElementById("aiIncome").value);
  const fixed_expenses = parseFloat(document.getElementById("aiFixedExpenses").value || 0);
  const variable_expenses = parseFloat(document.getElementById("aiVariableExpenses").value || 0);
  const goal = document.getElementById("aiGoal").value.trim();
  const savings_percentage = parseFloat(document.getElementById("aiSavingsPct").value || 25);

  const btn = document.getElementById("btnAiGenerateSubmit");
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Analyzing & Planning...</span>`;

  try {
    const res = await fetch("/api/ai/generate-budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ income, fixed_expenses, variable_expenses, goal, savings_percentage })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to generate AI budget");

    currentBudgetPlan = data.plan;
    displayAiPlanResults(currentBudgetPlan);
    closeModal("aiBudgetModal");
    showToast("AI Budget successfully generated!", "success");
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-bolt"></i> Generate Smart Budget`;
  }
}

function displayAiPlanResults(plan) {
  const container = document.getElementById("aiBudgetResultContainer");
  if (!container || !plan) return;

  document.getElementById("aiPlanNeeds").innerText = formatINR(plan.needs);
  document.getElementById("aiPlanWants").innerText = formatINR(plan.wants);
  document.getElementById("aiPlanSavings").innerText = formatINR(plan.savings);
  document.getElementById("aiPlanEmergency").innerText = formatINR(plan.emergency_fund);
  document.getElementById("aiPlanExplanation").innerText = plan.explanation;

  const tbody = document.getElementById("aiAllocationsTableBody");
  let html = "";
  (plan.category_allocations || []).forEach(cat => {
    html += `
      <tr>
        <td><strong style="color: #fff;">${cat.category}</strong></td>
        <td style="font-weight: 700; color: #60a5fa;">${formatINR(cat.amount)}</td>
        <td style="color: var(--text-muted); font-size: 13px;">${cat.tip || "-"}</td>
      </tr>
    `;
  });
  tbody.innerHTML = html;

  container.style.display = "block";
  container.scrollIntoView({ behavior: "smooth" });
}

async function applyAiPlanToDatabase() {
  if (!currentBudgetPlan || !currentBudgetPlan.category_allocations) {
    showToast("No active AI budget plan to apply.", "warning");
    return;
  }

  const month = document.getElementById("budgetMonth").value;
  const year = document.getElementById("budgetYear").value;
  const btn = document.getElementById("btnApplyAiPlan");

  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Applying...`;

  try {
    const res = await fetch("/api/budget/apply-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        allocations: currentBudgetPlan.category_allocations,
        month: month,
        year: year
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to apply plan");

    showToast(data.message, "success");
    loadBudgets();
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-check"></i> Apply This Plan to My Budget`;
  }
}
