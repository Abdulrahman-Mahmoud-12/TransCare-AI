/* ---------------------------------------------
   RetailIQ — Business Reports page
--------------------------------------------- */

const REPORTS_API = "/admin/reports";

const REPORT_TYPE_LABELS = {
  daily_sales: "Daily Sales Report",
  weekly_inventory: "Weekly Inventory Report",
  monthly_summary: "Monthly Business Summary",
  customer_insights: "Customer Insights Report",
  demand_forecast: "Demand Forecast Report",
};

const STATUS_CONFIG = {
  completed: { label: "Ready", className: "status-ready" },
  generating: { label: "Pending", className: "status-pending" },
  pending: { label: "Pending", className: "status-pending" },
  failed: { label: "Failed", className: "status-failed" },
};

function formatDisplayDate(isoString) {
  if (!isoString) return "—";
  const d = new Date(isoString);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function reportTypeLabel(reportType) {
  return REPORT_TYPE_LABELS[reportType] || reportType;
}

function statusConfig(status) {
  return STATUS_CONFIG[status] || { label: status, className: "status-pending" };
}

document.addEventListener("DOMContentLoaded", () => {
  const generateForm = document.getElementById("generateReportForm");
  const generateBtn = document.getElementById("generateReportBtn");
  const previewBtn = document.getElementById("previewReportBtn");
  const downloadPreviewBtn = document.getElementById("downloadPreviewBtn");
  const emailPreviewBtn = document.getElementById("emailPreviewBtn");
  const quickGenerateBtn = document.getElementById("quickGenerateBtn");
  const quickDownloadLatestBtn = document.getElementById("quickDownloadLatestBtn");
  const historyTable = document.getElementById("reportHistoryTable");
  const historyTableBody = historyTable?.querySelector("tbody");

  const lastReportPill = document.getElementById("lastReportPill");
  const previewReportName = document.getElementById("previewReportName");
  const previewReportMeta = document.getElementById("previewReportMeta");
  const previewSummaryText = document.getElementById("previewSummaryText");
  const previewStatusEl = document.querySelector(".preview-card .report-status");

  let lastGeneratedReportId = null;

  // ---------------------------------------------
  // Rendering helpers
  // ---------------------------------------------

  function renderPreviewCard(report) {
    if (previewReportName) previewReportName.textContent = report.title;
    if (previewReportMeta) {
      previewReportMeta.textContent =
        `${reportTypeLabel(report.report_type)} · Generated ${formatDisplayDate(report.created_at)}`;
    }
    if (previewStatusEl) {
      const cfg = statusConfig(report.status);
      previewStatusEl.textContent = cfg.label;
      previewStatusEl.className = `report-status ${cfg.className}`;
    }
    if (previewSummaryText) {
      previewSummaryText.textContent =
        report.status === "failed"
          ? `Generation failed: ${report.error_message || "Unknown error."}`
          : report.status === "completed"
          ? `Report generated successfully for the period ${formatDisplayDate(report.date_from)} – ${formatDisplayDate(report.date_to)}. Use the actions below to view or download it.`
          : "Report is still generating — refresh in a moment.";
    }
  }

  function updateLastGeneratedPill(report) {
    if (!lastReportPill) return;
    lastReportPill.textContent = `${report.title} · ${formatDisplayDate(report.created_at)}`;
  }

  function buildHistoryRow(report) {
    const tr = document.createElement("tr");
    const cfg = statusConfig(report.status);
    const isUsable = report.status === "completed";

    tr.innerHTML = `
      <td class="mono-cell">${report.id}</td>
      <td>${reportTypeLabel(report.report_type)}</td>
      <td>${formatDisplayDate(report.created_at)}</td>
      <td><span class="report-status ${cfg.className}">${cfg.label}</span></td>
      <td class="history-actions">
        <button class="icon-action-btn" title="View" ${isUsable ? "" : "disabled"}>👁</button>
        <button class="icon-action-btn" title="Download" ${isUsable ? "" : "disabled"}>⬇</button>
        <button class="icon-action-btn is-danger" title="Delete">🗑</button>
      </td>
    `;
    return tr;
  }

  function renderHistoryTable(reports) {
    if (!historyTableBody) return;
    historyTableBody.innerHTML = "";
    if (!reports.length) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td colspan="5" style="text-align:center;">No reports generated yet.</td>`;
      historyTableBody.appendChild(tr);
      return;
    }
    reports.forEach((report) => {
      historyTableBody.appendChild(buildHistoryRow(report));
    });
  }

  function prependHistoryRow(report) {
    if (!historyTableBody) return;
    // Remove the "no reports yet" row if present
    const emptyRow = historyTableBody.querySelector("td[colspan]");
    if (emptyRow) emptyRow.closest("tr").remove();
    historyTableBody.prepend(buildHistoryRow(report));
  }

  // Computes ISO date strings (YYYY-MM-DD) for each preset option
  function computeDateRange(preset) {
    const today = new Date();
    const toISODate = (d) => d.toISOString().slice(0, 10);
    let from = new Date(today);

    switch (preset) {
      case "today":
        break;
      case "this_week": {
        const day = today.getDay();
        from.setDate(today.getDate() - day);
        break;
      }
      case "this_month":
        from = new Date(today.getFullYear(), today.getMonth(), 1);
        break;
      case "last_30_days":
        from.setDate(today.getDate() - 30);
        break;
      default:
        return null;
    }
    return { date_from: `${toISODate(from)}T00:00:00`, date_to: `${toISODate(today)}T23:59:59` };
  }

  // ---------------------------------------------
  // Generate report
  // ---------------------------------------------
  generateForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(generateForm);

    const reportType = formData.get("report_type");
    const preset = formData.get("date_range_preset");
    const isCustom = preset === "custom";

    let dateFromVal = formData.get("date_from");
    let dateToVal = formData.get("date_to");

    if (!isCustom) {
      const computed = computeDateRange(preset);
      dateFromVal = computed.date_from;
      dateToVal = computed.date_to;
    }

    if (!reportType || !dateFromVal || !dateToVal) {
      alert("Please select a report type and a valid date range.");
      return;
    }

    const label = reportTypeLabel(reportType);
    const payload = {
      title: `${label} · ${dateFromVal} to ${dateToVal}`,
      report_type: reportType,
      date_from: dateFromVal,
      date_to: dateToVal,
    };

    generateBtn.disabled = true;
    generateBtn.textContent = "Generating…";

    try {
      const res = await fetch(`${REPORTS_API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${res.status})`);
      }

      const report = await res.json();
      lastGeneratedReportId = report.id;

      if (report.status === "failed") {
        console.error("Report generation failed:", report.error_message);
        renderPreviewCard(report); // still show the failure state, not silently swallow it
        alert(`Report generation failed: ${report.error_message}`);
      } else {
        renderPreviewCard(report);
        updateLastGeneratedPill(report);
        prependHistoryRow(report);
      }
    } catch (err) {
      console.error("Failed to generate report:", err);
      alert(`Failed to generate report: ${err.message}`);
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = "Generate Report";
    }
  });

  // Show/hide custom date inputs based on preset
  const presetSelect = document.getElementById("dateRangePreset");
  const dateFrom = document.getElementById("dateFrom");
  const dateTo = document.getElementById("dateTo");
  const syncDateInputs = () => {
    const isCustom = presetSelect?.value === "custom";
    if (dateFrom) dateFrom.disabled = !isCustom;
    if (dateTo) dateTo.disabled = !isCustom;
  };
  presetSelect?.addEventListener("change", syncDateInputs);
  syncDateInputs();

  // ---------------------------------------------
  // Preview card actions
  // ---------------------------------------------
  previewBtn?.addEventListener("click", async () => {
    if (!lastGeneratedReportId) return console.warn("No report to preview yet.");
    try {
      const res = await fetch(`${REPORTS_API}/${lastGeneratedReportId}`);
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const report = await res.json();
      renderPreviewCard(report);
    } catch (err) {
      console.error("Failed to load report:", err);
    }
  });

  downloadPreviewBtn?.addEventListener("click", () => {
    if (!lastGeneratedReportId) return console.warn("No report to download yet.");
    window.location.href = `${REPORTS_API}/${lastGeneratedReportId}/download`;
  });

  emailPreviewBtn?.addEventListener("click", () => {
    // TODO: no POST /{id}/email route or email_service.py implementation yet
    console.warn("Email endpoint not implemented in backend yet.");
  });

  // ---------------------------------------------
  // Quick actions
  // ---------------------------------------------
  quickGenerateBtn?.addEventListener("click", () => {
    document.getElementById("reportType")?.focus();
  });

  quickDownloadLatestBtn?.addEventListener("click", async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${REPORTS_API}?limit=1`);
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const reports = await res.json();
      if (!reports.length) return console.warn("No reports found.");
      window.location.href = `${REPORTS_API}/${reports[0].id}/download`;
    } catch (err) {
      console.error("Failed to download latest report:", err);
    }
  });

  // ---------------------------------------------
  // History table actions
  // ---------------------------------------------
  historyTable?.addEventListener("click", async (e) => {
    const btn = e.target.closest(".icon-action-btn");
    if (!btn || btn.disabled) return;
    const row = btn.closest("tr");
    const reportId = row?.querySelector(".mono-cell")?.textContent?.trim();
    const action = btn.title;

    if (!reportId) return;

    if (action === "View") {
      const res = await fetch(`${REPORTS_API}/${reportId}`);
      const report = await res.json();
      renderPreviewCard(report);
      lastGeneratedReportId = report.id;
    } else if (action === "Download") {
      window.location.href = `${REPORTS_API}/${reportId}/download`;
    } else if (action === "Delete") {
      // TODO: no DELETE /{id} route or delete_report() service function yet
      console.warn("Delete endpoint not implemented in backend yet.");
    }
  });

  // ---------------------------------------------
  // Load real history on page load — replaces static placeholder rows
  // ---------------------------------------------
  (async () => {
    try {
      const res = await fetch(`${REPORTS_API}?limit=50`);
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const reports = await res.json();
      renderHistoryTable(reports);

      if (reports.length) {
        updateLastGeneratedPill(reports[0]);
        renderPreviewCard(reports[0]);
        lastGeneratedReportId = reports[0].id;
      }
    } catch (err) {
      console.error("Failed to load report history:", err);
    }
  })();
});