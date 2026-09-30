// Main Shared JavaScript Utility for Personal Finance Advisor Bot

document.addEventListener("DOMContentLoaded", () => {
  // Mobile sidebar toggle
  const sidebar = document.getElementById("appSidebar");
  const toggleBtn = document.getElementById("sidebarToggle");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // Close sidebar on backdrop click on small screens
  document.addEventListener("click", (e) => {
    if (sidebar && sidebar.classList.contains("open")) {
      if (!sidebar.contains(e.target) && e.target !== toggleBtn && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    }
  });

  // Set today's date in quick modals
  const todayStr = new Date().toISOString().split("T")[0];
  const qeDate = document.getElementById("qeDate");
  const qiDate = document.getElementById("qiDate");
  if (qeDate && !qeDate.value) qeDate.value = todayStr;
  if (qiDate && !qiDate.value) qiDate.value = todayStr;
});

// Modal helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("show");
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("show");
  }
}

// Close modals when clicking backdrop
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.classList.remove("show");
  }
});

// Toast notification helper
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `alert alert-${type}`;
  toast.style.boxShadow = "0 8px 20px rgba(0,0,0,0.4)";
  toast.style.animation = "modalFadeIn 0.2s ease-out";
  toast.innerHTML = `
    <i class="fa-solid fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'circle-xmark' : type === 'warning' ? 'triangle-exclamation' : 'circle-info'}"></i>
    <div style="flex: 1;">${message}</div>
    <button style="background: none; border: none; color: inherit; cursor: pointer; padding: 2px;" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4000);
}

// Currency formatter
function formatINR(val) {
  const num = Number(val) || 0;
  return "₹" + num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

// Quick Expense Form Handler
async function handleQuickExpense(e) {
  e.preventDefault();
  const amount = parseFloat(document.getElementById("qeAmount").value);
  const category = document.getElementById("qeCategory").value;
  const payment_method = document.getElementById("qePayment").value;
  const date = document.getElementById("qeDate").value;
  const description = document.getElementById("qeDescription").value;

  try {
    const res = await fetch("/api/expenses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, category, payment_method, date, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to record expense");

    showToast("Expense recorded successfully!", "success");
    closeModal("quickExpenseModal");
    document.getElementById("quickExpenseForm").reset();
    document.getElementById("qeDate").value = new Date().toISOString().split("T")[0];

    // Trigger page-specific refresh if handler exists
    if (typeof loadDashboardData === "function") loadDashboardData();
    if (typeof loadExpenses === "function") loadExpenses();
    if (typeof loadTransactions === "function") loadTransactions();
    if (typeof loadBudgets === "function") loadBudgets();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

// Quick Income Form Handler
async function handleQuickIncome(e) {
  e.preventDefault();
  const amount = parseFloat(document.getElementById("qiAmount").value);
  const source = document.getElementById("qiSource").value;
  const date = document.getElementById("qiDate").value;
  const description = document.getElementById("qiDescription").value;

  try {
    const res = await fetch("/api/income", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, source, date, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to record income");

    showToast("Income added successfully!", "success");
    closeModal("quickIncomeModal");
    document.getElementById("quickIncomeForm").reset();
    document.getElementById("qiDate").value = new Date().toISOString().split("T")[0];

    // Trigger page-specific refresh if handler exists
    if (typeof loadDashboardData === "function") loadDashboardData();
    if (typeof loadIncomes === "function") loadIncomes();
    if (typeof loadTransactions === "function") loadTransactions();
  } catch (err) {
    showToast(err.message, "danger");
  }
}
