// AI Financial Advisor JavaScript Logic

document.addEventListener("DOMContentLoaded", () => {
  checkAiStatus();
});

async function checkAiStatus() {
  try {
    const res = await fetch("/api/ai/status");
    const data = await res.json();
    const engineSpan = document.getElementById("engineName");
    if (engineSpan && data.engine) {
      engineSpan.innerText = data.engine;
      if (data.is_live_gemini) {
        engineSpan.parentElement.className = "badge badge-normal";
      } else {
        engineSpan.parentElement.className = "badge badge-info";
      }
    }
  } catch (e) {
    console.error("AI status error:", e);
  }
}

function askPreset(question) {
  const input = document.getElementById("aiQuestionInput");
  if (input) {
    input.value = question;
    handleAskAi();
  }
}

async function handleAskAi() {
  const input = document.getElementById("aiQuestionInput");
  const question = input.value.trim();
  if (!question) {
    showToast("Please enter a question for the AI Advisor.", "warning");
    return;
  }

  const btn = document.getElementById("btnAskAi");
  const container = document.getElementById("aiResponseContainer");

  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Analyzing Finances...</span>`;

  // Temporary loading state in container
  container.innerHTML = `
    <div class="card" style="text-align: center; padding: 48px 24px;">
      <div style="font-size: 32px; color: var(--primary); margin-bottom: 16px;">
        <i class="fa-solid fa-brain fa-pulse"></i>
      </div>
      <h3 style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 8px;">Analyzing Your Financial Patterns</h3>
      <p style="font-size: 13.5px; color: var(--text-muted); max-width: 480px; margin: 0 auto;">
        Synthesizing monthly cash flow, category budgets, and savings goals to create your tailored recommendation...
      </p>
    </div>
  `;

  try {
    const res = await fetch("/api/ai/advice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.error || "Failed to generate financial advice");

    renderAiAdviceCard(result.question, result.data);
  } catch (err) {
    showToast(err.message, "danger");
    container.innerHTML = `
      <div class="alert alert-danger">
        <i class="fa-solid fa-circle-exclamation"></i>
        <div>${err.message}</div>
      </div>
    `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Ask Advisor</span>`;
  }
}

function renderAiAdviceCard(question, data) {
  const container = document.getElementById("aiResponseContainer");
  if (!container || !data) return;

  const actionSteps = data.action_steps || [];
  let actionStepsHtml = "";
  actionSteps.forEach(step => {
    actionStepsHtml += `<li>${step}</li>`;
  });

  const engineLabel = data.source || "Google Gemini";

  container.innerHTML = `
    <div class="ai-response-card" style="animation: modalFadeIn 0.3s ease-out;">
      <div class="ai-header">
        <div class="ai-header-brand">
          <i class="fa-solid fa-robot"></i>
          <span>Financial Strategy Report</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="badge badge-info" style="font-size: 11px;">${engineLabel}</span>
          <span style="font-size: 12px; color: var(--text-dim);">${new Date().toLocaleDateString("en-IN")}</span>
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
        <span style="font-size: 11px; text-transform: uppercase; color: var(--text-dim); font-weight: 700;">Query Addressed:</span>
        <div style="font-size: 15px; font-weight: 600; color: #fff; margin-top: 2px;">"${question}"</div>
      </div>

      <!-- 1. AI Insight -->
      <div class="ai-section">
        <div class="ai-section-title" style="color: #60a5fa;">
          <i class="fa-solid fa-eye"></i> AI Insight
        </div>
        <div class="ai-section-content">
          ${data.insight}
        </div>
      </div>

      <!-- 2. Problem Identified -->
      <div class="ai-section">
        <div class="ai-section-title" style="color: #f87171;">
          <i class="fa-solid fa-triangle-exclamation"></i> Problem Identified
        </div>
        <div class="ai-section-content" style="color: #fca5a5;">
          ${data.problem}
        </div>
      </div>

      <!-- 3. Recommendation -->
      <div class="ai-section">
        <div class="ai-section-title" style="color: #34d399;">
          <i class="fa-solid fa-lightbulb"></i> Core Recommendation
        </div>
        <div class="ai-section-content">
          ${data.recommendation}
        </div>
      </div>

      <!-- 4. Action Steps -->
      <div class="ai-section" style="margin-bottom: 0;">
        <div class="ai-section-title" style="color: #fbbf24;">
          <i class="fa-solid fa-list-check"></i> Immediate Action Steps
        </div>
        <ul class="ai-action-list">
          ${actionStepsHtml}
        </ul>
      </div>
    </div>
  `;
}
