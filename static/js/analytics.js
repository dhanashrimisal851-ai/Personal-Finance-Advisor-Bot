// Spending Analytics JavaScript Logic with Chart.js

let doughnutChartInstance = null;
let barChartInstance = null;
let lineChartInstance = null;

const CHART_COLORS = [
  "#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444",
  "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#64748b"
];

document.addEventListener("DOMContentLoaded", () => {
  const now = new Date();
  const mSelect = document.getElementById("analyticsMonth");
  const ySelect = document.getElementById("analyticsYear");
  if (mSelect) mSelect.value = String(now.getMonth() + 1);
  if (ySelect) ySelect.value = String(now.getFullYear());

  loadAnalytics();
});

async function loadAnalytics() {
  const month = document.getElementById("analyticsMonth").value;
  const year = document.getElementById("analyticsYear").value;

  try {
    const res = await fetch(`/api/analytics?month=${month}&year=${year}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load analytics");

    renderDoughnutChart(data.category_distribution || []);
    renderTopSpending(data.top_spending || []);
    renderBarChart(data.trends || {});
    renderLineChart(data.trends || {});
    renderComparisonTable(data.category_comparison || []);

  } catch (err) {
    showToast(err.message, "danger");
  }
}

// 1. Expense Distribution Doughnut Chart
function renderDoughnutChart(distribution) {
  const ctx = document.getElementById("categoryDoughnutChart");
  if (!ctx) return;

  if (doughnutChartInstance) {
    doughnutChartInstance.destroy();
  }

  if (distribution.length === 0) {
    distribution = [{ category: "No Expenses", amount: 1 }];
  }

  const labels = distribution.map(d => d.category);
  const values = distribution.map(d => d.amount);

  doughnutChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: CHART_COLORS.slice(0, labels.length),
        borderColor: "#162032",
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#94a3b8",
            boxWidth: 12,
            font: { family: "Inter", size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const val = context.raw || 0;
              return ` ${label}: ₹${Number(val).toLocaleString('en-IN')}`;
            }
          }
        }
      },
      cutout: "68%"
    }
  });
}

// 2. Top Spending Categories Ranked
function renderTopSpending(topList) {
  const container = document.getElementById("topSpendingContainer");
  if (!container) return;

  if (topList.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 30px;">
        No spending recorded for this month.
      </div>
    `;
    return;
  }

  let html = "";
  topList.forEach((item, idx) => {
    html += `
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <div style="width: 28px; height: 28px; border-radius: 50%; background: rgba(59, 130, 246, 0.15); color: #60a5fa; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center;">
            ${idx + 1}
          </div>
          <div>
            <strong style="color: #fff; font-size: 14px;">${item.category}</strong>
            <div style="font-size: 12px; color: var(--text-dim);">${item.percentage}% of total expenses</div>
          </div>
        </div>
        <div style="font-size: 16px; font-weight: 700; color: #f87171;">
          ${formatINR(item.amount)}
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

// 3. Monthly Income vs Expenses Bar Chart
function renderBarChart(trends) {
  const ctx = document.getElementById("incomeVsExpenseBarChart");
  if (!ctx) return;

  if (barChartInstance) {
    barChartInstance.destroy();
  }

  barChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: trends.labels || [],
      datasets: [
        {
          label: "Income",
          data: trends.income || [],
          backgroundColor: "rgba(16, 185, 129, 0.75)",
          borderColor: "#10b981",
          borderWidth: 1,
          borderRadius: 6
        },
        {
          label: "Expenses",
          data: trends.expenses || [],
          backgroundColor: "rgba(239, 68, 68, 0.75)",
          borderColor: "#ef4444",
          borderWidth: 1,
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { family: "Inter", size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#64748b" },
          grid: { color: "rgba(255,255,255,0.04)" }
        },
        y: {
          ticks: {
            color: "#64748b",
            callback: (v) => "₹" + Number(v).toLocaleString("en-IN")
          },
          grid: { color: "rgba(255,255,255,0.04)" }
        }
      }
    }
  });
}

// 4. Savings Trend Line Chart
function renderLineChart(trends) {
  const ctx = document.getElementById("savingsTrendLineChart");
  if (!ctx) return;

  if (lineChartInstance) {
    lineChartInstance.destroy();
  }

  lineChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: trends.labels || [],
      datasets: [{
        label: "Net Savings",
        data: trends.savings || [],
        borderColor: "#06b6d4",
        backgroundColor: "rgba(6, 182, 212, 0.15)",
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "#06b6d4",
        pointBorderColor: "#fff",
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { family: "Inter", size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Savings: ₹${Number(ctx.raw).toLocaleString('en-IN')}`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#64748b" },
          grid: { color: "rgba(255,255,255,0.04)" }
        },
        y: {
          ticks: {
            color: "#64748b",
            callback: (v) => "₹" + Number(v).toLocaleString("en-IN")
          },
          grid: { color: "rgba(255,255,255,0.04)" }
        }
      }
    }
  });
}

// 5. Month-over-Month Category Comparison Table
function renderComparisonTable(comparison) {
  const tbody = document.getElementById("comparisonTableBody");
  if (!tbody) return;

  if (comparison.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">
          No comparison data available for these months.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  comparison.forEach(c => {
    const isIncrease = c.difference > 0;
    const diffColor = isIncrease ? "#f87171" : "#34d399";
    const diffPrefix = isIncrease ? "+" : "";

    html += `
      <tr>
        <td><strong style="color: #fff;">${c.category}</strong></td>
        <td style="text-align: right; color: var(--text-muted);">${formatINR(c.previous_amount)}</td>
        <td style="text-align: right; color: #fff; font-weight: 600;">${formatINR(c.current_amount)}</td>
        <td style="text-align: right; font-weight: 700; color: ${diffColor};">
          ${diffPrefix}${formatINR(c.difference)}
        </td>
        <td style="text-align: right;">
          <span class="badge ${isIncrease ? 'badge-danger' : 'badge-normal'}" style="font-size: 11px;">
            ${diffPrefix}${c.percentage_change}%
          </span>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}
