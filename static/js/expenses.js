// Expense Management JavaScript Logic

let currentExpenses = [];
let activeViewMode = null;
let searchDebounceTimeout = null;

document.addEventListener("DOMContentLoaded", () => {
  loadExpenses();
});

function setViewMode(mode) {
  activeViewMode = mode;
  document.getElementById("btnModeAll").classList.toggle("btn-primary", mode === null);
  document.getElementById("btnModeWeekly").classList.toggle("btn-primary", mode === "weekly");
  document.getElementById("btnModeMonthly").classList.toggle("btn-primary", mode === "monthly");
  loadExpenses();
}

function debounceLoadExpenses() {
  clearTimeout(searchDebounceTimeout);
  searchDebounceTimeout = setTimeout(() => {
    loadExpenses();
  }, 300);
}

async function loadExpenses() {
  const category = document.getElementById("filterExpenseCategory").value;
  const payment = document.getElementById("filterExpensePayment").value;
  const startDate = document.getElementById("filterExpenseStart").value;
  const endDate = document.getElementById("filterExpenseEnd").value;
  const search = document.getElementById("searchExpense").value.trim();
  const sortBy = document.getElementById("sortExpense").value;

  let url = `/api/expenses?sort_by=${sortBy}`;
  if (category && category !== "All") url += `&category=${encodeURIComponent(category)}`;
  if (payment && payment !== "All") url += `&payment_method=${encodeURIComponent(payment)}`;
  if (startDate) url += `&start_date=${startDate}`;
  if (endDate) url += `&end_date=${endDate}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (activeViewMode) url += `&view_mode=${activeViewMode}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load expenses");

    currentExpenses = data.expenses || [];

    document.getElementById("expenseTotalDisplay").innerText = formatINR(data.total_amount);
    document.getElementById("expenseCountDisplay").innerText = `${currentExpenses.length} recorded entries`;

    renderExpenseTable(currentExpenses);
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function renderExpenseTable(expenses) {
  const tbody = document.getElementById("expenseTableBody");
  if (!tbody) return;

  if (expenses.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 36px;">
          No expense entries found matching criteria.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  expenses.forEach(exp => {
    html += `
      <tr>
        <td style="color: var(--text-muted); font-size: 13.5px;">${exp.date}</td>
        <td>
          <strong style="color: #fff;">${exp.category}</strong>
        </td>
        <td style="color: var(--text-main); font-size: 13.5px;">${exp.description || "-"}</td>
        <td>
          <span class="badge badge-info" style="font-size: 11px;">${exp.payment_method}</span>
        </td>
        <td style="text-align: right; font-weight: 700; color: #f87171; font-size: 15px;">
          - ${formatINR(exp.amount)}
        </td>
        <td style="text-align: center;">
          <button class="btn btn-secondary btn-icon btn-sm" onclick="openEditExpenseModal(${exp.id})" title="Edit">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button class="btn btn-danger btn-icon btn-sm" onclick="deleteExpense(${exp.id})" title="Delete" style="margin-left: 4px;">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function openEditExpenseModal(id) {
  const exp = currentExpenses.find(e => e.id === id);
  if (!exp) return;

  document.getElementById("editExpenseId").value = exp.id;
  document.getElementById("editExpenseAmount").value = exp.amount;
  document.getElementById("editExpenseCategory").value = exp.category;
  document.getElementById("editExpensePayment").value = exp.payment_method || "UPI";
  document.getElementById("editExpenseDate").value = exp.date;
  document.getElementById("editExpenseDescription").value = exp.description || "";

  openModal("editExpenseModal");
}

async function handleEditExpense(e) {
  e.preventDefault();
  const id = document.getElementById("editExpenseId").value;
  const amount = parseFloat(document.getElementById("editExpenseAmount").value);
  const category = document.getElementById("editExpenseCategory").value;
  const payment_method = document.getElementById("editExpensePayment").value;
  const date = document.getElementById("editExpenseDate").value;
  const description = document.getElementById("editExpenseDescription").value;

  try {
    const res = await fetch(`/api/expenses/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, category, payment_method, date, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to update expense");

    showToast("Expense updated successfully!", "success");
    closeModal("editExpenseModal");
    loadExpenses();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

async function deleteExpense(id) {
  if (!confirm("Are you sure you want to delete this expense record?")) return;

  try {
    const res = await fetch(`/api/expenses/${id}`, {
      method: "DELETE"
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete expense");

    showToast("Expense deleted.", "info");
    loadExpenses();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function resetExpenseFilters() {
  document.getElementById("filterExpenseCategory").value = "All";
  document.getElementById("filterExpensePayment").value = "All";
  document.getElementById("filterExpenseStart").value = "";
  document.getElementById("filterExpenseEnd").value = "";
  document.getElementById("searchExpense").value = "";
  document.getElementById("sortExpense").value = "date_desc";
  activeViewMode = null;
  loadExpenses();
}
