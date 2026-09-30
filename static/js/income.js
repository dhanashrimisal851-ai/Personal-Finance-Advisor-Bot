// Income Management JavaScript Logic

let currentIncomes = [];

document.addEventListener("DOMContentLoaded", () => {
  loadIncomes();
});

async function loadIncomes() {
  const source = document.getElementById("filterIncomeSource").value;
  const startDate = document.getElementById("filterIncomeStart").value;
  const endDate = document.getElementById("filterIncomeEnd").value;
  const sortBy = document.getElementById("sortIncome").value;

  let url = `/api/income?sort_by=${sortBy}`;
  if (source && source !== "All") url += `&source=${encodeURIComponent(source)}`;
  if (startDate) url += `&start_date=${startDate}`;
  if (endDate) url += `&end_date=${endDate}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load income records");

    currentIncomes = data.incomes || [];

    document.getElementById("incomeTotalDisplay").innerText = formatINR(data.total_amount);
    document.getElementById("incomeCountDisplay").innerText = `${currentIncomes.length} recorded entries`;

    renderIncomeTable(currentIncomes);
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function renderIncomeTable(incomes) {
  const tbody = document.getElementById("incomeTableBody");
  if (!tbody) return;

  if (incomes.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 36px;">
          No income entries found matching criteria.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  incomes.forEach(inc => {
    html += `
      <tr>
        <td style="color: var(--text-muted); font-size: 13.5px;">${inc.date}</td>
        <td>
          <span class="badge badge-normal">${inc.source}</span>
        </td>
        <td style="color: var(--text-main); font-size: 13.5px;">${inc.description || "-"}</td>
        <td style="text-align: right; font-weight: 700; color: #34d399; font-size: 15px;">
          + ${formatINR(inc.amount)}
        </td>
        <td style="text-align: center;">
          <button class="btn btn-secondary btn-icon btn-sm" onclick="openEditIncomeModal(${inc.id})" title="Edit">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button class="btn btn-danger btn-icon btn-sm" onclick="deleteIncome(${inc.id})" title="Delete" style="margin-left: 4px;">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function openAddIncomeModal() {
  openModal("quickIncomeModal");
}

function openEditIncomeModal(id) {
  const inc = currentIncomes.find(i => i.id === id);
  if (!inc) return;

  document.getElementById("editIncomeId").value = inc.id;
  document.getElementById("editIncomeAmount").value = inc.amount;
  document.getElementById("editIncomeSource").value = inc.source;
  document.getElementById("editIncomeDate").value = inc.date;
  document.getElementById("editIncomeDescription").value = inc.description || "";

  openModal("editIncomeModal");
}

async function handleEditIncome(e) {
  e.preventDefault();
  const id = document.getElementById("editIncomeId").value;
  const amount = parseFloat(document.getElementById("editIncomeAmount").value);
  const source = document.getElementById("editIncomeSource").value;
  const date = document.getElementById("editIncomeDate").value;
  const description = document.getElementById("editIncomeDescription").value;

  try {
    const res = await fetch(`/api/income/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, source, date, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to update income");

    showToast("Income record updated successfully!", "success");
    closeModal("editIncomeModal");
    loadIncomes();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

async function deleteIncome(id) {
  if (!confirm("Are you sure you want to delete this income entry?")) return;

  try {
    const res = await fetch(`/api/income/${id}`, {
      method: "DELETE"
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to delete income");

    showToast("Income entry deleted.", "info");
    loadIncomes();
  } catch (err) {
    showToast(err.message, "danger");
  }
}

function resetIncomeFilters() {
  document.getElementById("filterIncomeSource").value = "All";
  document.getElementById("filterIncomeStart").value = "";
  document.getElementById("filterIncomeEnd").value = "";
  document.getElementById("sortIncome").value = "date_desc";
  loadIncomes();
}
