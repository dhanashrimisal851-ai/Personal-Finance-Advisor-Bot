// Dashboard JavaScript Logic

document.addEventListener("DOMContentLoaded", () => {
  // Initialize month and year selectors with current date
  const now = new Date();
  const monthSelect = document.getElementById("dashMonth");
  const yearSelect = document.getElementById("dashYear");

  if (monthSelect) monthSelect.value = String(now.getMonth() + 1);
  if (yearSelect) yearSelect.value = String(now.getFullYear());

  loadDashboardData();
});

async function loadDashboardData() {
  const month = document.getElementById("dashMonth").value;
  const year = document.getElementById("dashYear").value;

  try {
    const res = await fetch(`/api/dashboard?month=${month}&year=${year}`);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Failed to load dashboard data");

    // 1. Update 5 Summary Metric Cards
    document.getElementById("cardIncome").innerText = formatINR(data.finances.monthly_income);
    document.getElementById("cardExpenses").innerText = formatINR(data.finances.total_expenses);
    document.getElementById("cardSavings").innerText = formatINR(data.finances.current_savings);
    document.getElementById("cardSavingsRate").innerText = `${data.finances.savings_percentage}%`;
    document.getElementById("cardRemainingBudget").innerText = formatINR(data.finances.remaining_budget);

    // Negative savings warning text
    if (data.finances.current_savings < 0) {
      document.getElementById("cardSavings").style.color = "#f87171";
    } else {
      document.getElementById("cardSavings").style.color = "#22d3ee";
    }

    // 2. Render In-App Alerts
    renderAlerts(data.alerts || []);

    // 3. Render Financial Health Score
    renderHealthScore(data.health_score);

    // 4. Render Budget Adherence Progress Bars
    renderBudgetPerformance(data.budget_performance);

    // 5. Render Recent Transactions Table
    renderRecentTransactions(data.recent_transactions || []);

    // 6. Render Active Savings Goals
    renderDashboardGoals(data.goals || []);

  } catch (err) {
    showToast(err.message, "danger");
  }
}

function renderAlerts(alerts) {
  const container = document.getElementById("dashboardAlerts");
  if (!container) return;

  if (alerts.length === 0) {
    container.innerHTML = "";
    return;
  }

  let html = "";
  alerts.forEach(a => {
    html += `
      <div class="alert alert-${a.type}" style="margin-bottom: 10px;">
        <i class="fa-solid fa-${a.icon}"></i>
        <div style="flex: 1;">
          <strong>${a.title}:</strong> ${a.message}
        </div>
      </div>
    `;
  });
  container.innerHTML = html;
}

function renderHealthScore(health) {
  if (!health) return;

  const scoreVal = document.getElementById("healthScoreValue");
  const scoreBadge = document.getElementById("healthScoreBadge");
  const scoreSummary = document.getElementById("healthScoreSummary");
  const positivesList = document.getElementById("healthPositives");
  const improveList = document.getElementById("healthImprovements");

  scoreVal.innerText = health.score;

  let badgeClass = "badge-normal";
  if (health.score < 40) badgeClass = "badge-danger";
  else if (health.score < 70) badgeClass = "badge-warning";

  scoreBadge.className = `badge ${badgeClass}`;
  scoreBadge.innerText = health.badge;

  scoreSummary.innerText = health.summary;

  // Positives
  if (health.positive_habits && health.positive_habits.length > 0) {
    positivesList.innerHTML = health.positive_habits.map(h => `<li>${h}</li>`).join("");
  } else {
    positivesList.innerHTML = `<li style="color: var(--text-dim);">No distinct positive habits identified yet.</li>`;
  }

  // Improvements
  if (health.areas_to_improve && health.areas_to_improve.length > 0) {
    improveList.innerHTML = health.areas_to_improve.map(i => `<li>${i}</li>`).join("");
  } else {
    improveList.innerHTML = `<li style="color: #34d399;">Great job! No major immediate risk areas identified.</li>`;
  }
}

function renderBudgetPerformance(budgetPerf) {
  const list = document.getElementById("budgetProgressList");
  if (!list) return;

  const items = budgetPerf.items || [];
  if (items.length === 0) {
    list.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 24px 0;">
        <i class="fa-solid fa-chart-pie" style="font-size: 32px; color: var(--text-dim); margin-bottom: 12px; display: block;"></i>
        No category budgets set for this month.<br>
        <a href="/budget" class="btn btn-primary btn-sm" style="margin-top: 12px;">+ Set Monthly Budget</a>
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
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 13.5px;">
          <div>
            <strong style="color: #fff;">${b.category}</strong>
            <span style="font-size: 12px; color: var(--text-dim); margin-left: 6px;">(${formatINR(b.spent)} / ${formatINR(b.budget)})</span>
          </div>
          <div>
            <span class="badge ${badgeColor}">${b.percentage}% Used</span>
          </div>
        </div>
        <div class="progress">
          <div class="progress-bar ${barColor}" style="width: ${cappedPct}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11.5px; color: var(--text-dim); margin-top: 4px;">
          <span>Remaining: ${formatINR(b.remaining)}</span>
          <span style="color: ${b.status === 'danger' ? '#f87171' : b.status === 'warning' ? '#fbbf24' : '#34d399'};">${b.status_text}</span>
        </div>
      </div>
    `;
  });

  list.innerHTML = html;
}

function renderRecentTransactions(txs) {
  const tbody = document.getElementById("recentTransactionsTable");
  if (!tbody) return;

  if (txs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">
          No transactions recorded yet. Use the top buttons to add your first income or expense!
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  txs.forEach(t => {
    const isIncome = t.type === "Income";
    const amtColor = isIncome ? "#34d399" : "#f87171";
    const amtPrefix = isIncome ? "+" : "-";
    const badgeType = isIncome ? "badge-normal" : "badge-info";

    html += `
      <tr>
        <td style="color: var(--text-muted); font-size: 13px;">${t.date}</td>
        <td><span class="badge ${badgeType}">${t.type}</span></td>
        <td><strong style="color: #fff;">${t.category}</strong></td>
        <td style="color: var(--text-muted); font-size: 13px;">${t.description || "-"}</td>
        <td style="text-align: right; font-weight: 700; color: ${amtColor}; font-size: 14.5px;">
          ${amtPrefix} ${formatINR(t.amount)}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function renderDashboardGoals(goals) {
  const container = document.getElementById("dashboardGoalsList");
  if (!container) return;

  if (goals.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 24px 0;">
        <i class="fa-solid fa-bullseye" style="font-size: 32px; color: var(--text-dim); margin-bottom: 12px; display: block;"></i>
        No active savings goals found.<br>
        <a href="/goals" class="btn btn-outline btn-sm" style="margin-top: 12px;">+ Set a Goal</a>
      </div>
    `;
    return;
  }

  let html = "";
  goals.forEach(g => {
    html += `
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong style="color: #fff; font-size: 14px;">${g.name}</strong>
          <span style="font-size: 12.5px; font-weight: 600; color: #fbbf24;">${g.progress_percentage}%</span>
        </div>
        <div class="progress" style="margin-bottom: 8px;">
          <div class="progress-bar normal" style="width: ${Math.min(g.progress_percentage, 100)}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted);">
          <span>Saved: <b style="color: #fff;">${formatINR(g.current_amount)}</b></span>
          <span>Target: <b style="color: #fff;">${formatINR(g.target_amount)}</b></span>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}
