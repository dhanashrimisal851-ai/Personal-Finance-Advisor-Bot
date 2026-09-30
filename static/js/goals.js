// Savings Goals & Calculator JavaScript Logic

let currentGoals = [];

document.addEventListener("DOMContentLoaded", () => {
  loadGoals();
});

async function loadGoals() {
  try {
    const res = await fetch("/api/goals");
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load goals");

    currentGoals = data.goals || [];
    const summary = data.summary || {};

    document.getElementById("summaryTotalTarget").innerText = formatINR(summary.total_target);
    document.getElementById("summaryTotalSaved").innerText = formatINR(summary.total_saved);
    document.getElementById("summaryOverallProgress").innerText = `${summary.overall_progress}%`;
    document.getElementById("summaryGoalsCount").innerText = `${summary.goals_count} active goals`;

    renderGoalsGrid(currentGoals);
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function renderGoalsGrid(goals) {
  const container = document.getElementById("goalsContainer");
  if (!container) return;

  if (goals.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 48px; grid-column: 1 / -1;">
        <i class="fa-solid fa-bullseye" style="font-size: 38px; color: var(--text-dim); margin-bottom: 14px; display: block;"></i>
        No savings goals created yet.<br>
        Click "Create Savings Goal" to define your targets!
      </div>
    `;
    return;
  }

  let html = "";
  goals.forEach(g => {
    const isCompleted = g.progress_percentage >= 100;
    const badgeColor = isCompleted ? "badge-normal" : "badge-warning";
    const statusText = isCompleted ? "Goal Achieved!" : `${g.progress_percentage}% Saved`;

    html += `
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 22px; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <div>
              <h3 style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 3px;">${g.name}</h3>
              <span class="badge ${badgeColor}">${statusText}</span>
            </div>
            <div style="display: flex; gap: 4px;">
              <button class="btn btn-success btn-icon btn-sm" onclick="openContributeModal(${g.id}, '${g.name}')" title="Deposit Funds">
                <i class="fa-solid fa-plus"></i>
              </button>
              <button class="btn btn-danger btn-icon btn-sm" onclick="deleteGoal(${g.id})" title="Delete Goal">
                <i class="fa-solid fa-trash"></i>
              </button>
            </div>
          </div>

          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
            ${g.description || "Personal financial objective"}
          </p>

          <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
              <span>Saved: <b style="color: #34d399;">${formatINR(g.current_amount)}</b></span>
              <span>Target: <b style="color: #fff;">${formatINR(g.target_amount)}</b></span>
            </div>
            <div class="progress" style="height: 10px;">
              <div class="progress-bar normal" style="width: ${Math.min(g.progress_percentage, 100)}%;"></div>
            </div>
          </div>
        </div>

        <div style="padding-top: 12px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-dim);">
          <span>Remaining: <b style="color: #60a5fa;">${formatINR(g.remaining_amount)}</b></span>
          <span>Target Date: <b style="color: #fff;">${g.target_date || "No deadline"}</b></span>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

async function handleCreateGoal(e) {
  e.preventDefault();
  const name = document.getElementById("goalName").value.trim();
  const target_amount = parseFloat(document.getElementById("goalTarget").value);
  const current_amount = parseFloat(document.getElementById("goalCurrent").value || 0);
  const target_date = document.getElementById("goalTargetDate").value;
  const description = document.getElementById("goalDescription").value.trim();

  try {
    const res = await fetch("/api/goals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, target_amount, current_amount, target_date, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to create goal");

    showToast(data.message, "success");
    closeModal("addGoalModal");
    document.getElementById("addGoalForm").reset();
    loadGoals();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function openContributeModal(id, name) {
  document.getElementById("contributeGoalId").value = id;
  document.getElementById("contributeGoalNamePrompt").innerText = `Deposit savings towards '${name}':`;
  document.getElementById("contributeAmount").value = "";
  openModal("contributeGoalModal");
}

async function handleContributeGoal(e) {
  e.preventDefault();
  const id = document.getElementById("contributeGoalId").value;
  const amount = parseFloat(document.getElementById("contributeAmount").value);

  try {
    const res = await fetch(`/api/goals/${id}/contribute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to add funds");

    showToast(data.message, "success");
    closeModal("contributeGoalModal");
    loadGoals();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

async function deleteGoal(id) {
  if (!confirm("Are you sure you want to delete this goal?")) return;

  try {
    const res = await fetch(`/api/goals/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete goal");

    showToast("Goal deleted.", "info");
    loadGoals();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

// Savings Calculator Execution
async function calculateSavings() {
  const goal_amount = parseFloat(document.getElementById("calcGoalAmount").value);
  const current_savings = parseFloat(document.getElementById("calcCurrentSavings").value || 0);
  const monthly_contribution = parseFloat(document.getElementById("calcMonthlyContribution").value || 0);
  const target_date = document.getElementById("calcTargetDate").value;

  try {
    const res = await fetch("/api/goals/calculator", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal_amount, current_savings, monthly_contribution, target_date })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Calculation failed");

    const c = data.calculation;
    document.getElementById("calcResRemaining").innerText = formatINR(c.remaining_amount);
    
    if (c.estimated_months_to_complete) {
      document.getElementById("calcResMonths").innerText = `${c.estimated_months_to_complete} Month${c.estimated_months_to_complete > 1 ? 's' : ''}`;
    } else {
      document.getElementById("calcResMonths").innerText = "Enter contribution";
    }

    if (c.estimated_completion_date) {
      document.getElementById("calcResDate").innerText = c.estimated_completion_date;
      document.getElementById("calcResDateContainer").style.display = "block";
    } else {
      document.getElementById("calcResDateContainer").style.display = "none";
    }

    if (c.required_monthly_savings) {
      document.getElementById("calcResRequired").innerText = `${formatINR(c.required_monthly_savings)} / month`;
      document.getElementById("calcResRequiredMonthlyContainer").style.display = "block";
    } else {
      document.getElementById("calcResRequiredMonthlyContainer").style.display = "none";
    }

    document.getElementById("calcResults").style.display = "block";
  } catch (err) {
    showToast(err.message, "danger");
  }
}
