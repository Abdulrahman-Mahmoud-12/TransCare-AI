/* ==========================================================
   RetailIQ — Admin Shelf Monitoring interactions
   Wired to app/routers/shelf_monitoring.py
   Every result section below is rendered from the real API
   response — nothing here is hardcoded/placeholder data.
   ========================================================== */

(function () {
  // -----------------------------------------------------------
  // Element refs
  // -----------------------------------------------------------
  const dropzone = document.getElementById("uploadDropzone");
  const dropzoneInner = document.getElementById("uploadDropzoneInner");
  const fileInput = document.getElementById("shelfFileInput");
  const browseBtn = document.getElementById("browseImageBtn");

  const previewWrap = document.getElementById("uploadPreview");
  const previewImg = document.getElementById("uploadPreviewImg");
  const fileNameEl = document.getElementById("uploadFileName");
  const fileSizeEl = document.getElementById("uploadFileSize");

  const statusDot = document.getElementById("uploadStatusDot");
  const statusText = document.getElementById("uploadStatusText");

  const uploadImageBtn = document.getElementById("uploadImageBtn");
  const analyzeBtn = document.getElementById("analyzeShelfBtn");
  const resetBtn = document.getElementById("resetUploadBtn");

  const progressWrap = document.getElementById("analyzeProgress");
  const progressFill = document.getElementById("analyzeProgressFill");
  const progressText = document.getElementById("analyzeProgressText");

  const resultsWrapper = document.getElementById("resultsWrapper");
  const originalImageEl = document.getElementById("originalImageEl");
  const detectionImageEl = document.getElementById("detectionImageEl");
  const bboxLayer = document.getElementById("bboxLayer");
  const lastAnalysisTimeEl = document.getElementById("lastAnalysisTime");
  const doughnutChart = document.getElementById("doughnutChart");
  const doughnutPct = document.getElementById("doughnutPct");
  const legendOccupiedPct = document.getElementById("legendOccupiedPct");
  const legendEmptyPct = document.getElementById("legendEmptyPct");

  // KPI + table elements
  const kpiTotalProducts = document.getElementById("kpiTotalProducts");
  const kpiEmptySpaces = document.getElementById("kpiEmptySpaces");
  const kpiOccupancy = document.getElementById("kpiOccupancy");
  const kpiClasses = document.getElementById("kpiClasses");
  const kpiConfidence = document.getElementById("kpiConfidence");
  const detectionTableBody = document.getElementById("detectionTableBody");

  // Bar chart / stats / insights / recent analyses
  const barChartBars = document.getElementById("barChartBars");
  const statMostDetected = document.getElementById("statMostDetected");
  const statLeastDetected = document.getElementById("statLeastDetected");
  const statEmptySections = document.getElementById("statEmptySections");
  const statTotalCapacity = document.getElementById("statTotalCapacity");
  const statProcessingTime = document.getElementById("statProcessingTime");
  const insightsGrid = document.getElementById("insightsGrid");
  const recentAnalysesBody = document.getElementById("recentAnalysesBody");

  const BAR_PALETTE = ["#6366f1", "#c8830f", "#1fa15a", "#c8461e", "#7fe8d9", "#2c3b57", "#9b59b6", "#e67e22", "#e74c3c", "#16a085"];

  let selectedFile = null;
  let objectUrl = null;
  let currentAnalysisId = null; // e.g. "SM-1043"

  // -----------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------
  function formatBytes(bytes) {
    if (!bytes) return "—";
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(2)} MB`;
  }

  function setStatus(state, text) {
    statusDot.className = "upload-status-dot" + (state ? ` is-${state}` : "");
    statusText.textContent = text;
  }

  function resetUI() {
    selectedFile = null;
    currentAnalysisId = null;
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = null;

    fileInput.value = "";
    previewWrap.hidden = true;
    dropzoneInner.hidden = false;
    dropzone.classList.remove("is-dragover");

    uploadImageBtn.disabled = true;
    analyzeBtn.disabled = true;
    progressWrap.hidden = true;
    progressFill.style.width = "0%";

    resultsWrapper.hidden = true;

    setStatus(null, "No image selected yet.");
  }

  // -----------------------------------------------------------
  // File selection (browse + drag/drop)
  // -----------------------------------------------------------
  function handleFile(file) {
    if (!file) return;
    const validTypes = ["image/jpeg", "image/png", "image/jpg"];
    if (!validTypes.includes(file.type)) {
      setStatus("selected", "Unsupported file type. Please use JPG, PNG, or JPEG.");
      return;
    }

    selectedFile = file;
    currentAnalysisId = null;
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = URL.createObjectURL(file);

    previewImg.src = objectUrl;
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatBytes(file.size);

    dropzoneInner.hidden = true;
    previewWrap.hidden = false;

    uploadImageBtn.disabled = false;
    analyzeBtn.disabled = true; // must upload before analyzing
    resultsWrapper.hidden = true;

    setStatus("selected", "Image selected — ready to upload.");
  }

  browseBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => handleFile(e.target.files[0]));

  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("is-dragover");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("is-dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    handleFile(file);
  });

  // -----------------------------------------------------------
  // Upload Image -> POST /api/shelf-monitoring/upload
  // -----------------------------------------------------------
  uploadImageBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    uploadImageBtn.disabled = true;
    setStatus("selected", "Uploading…");

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const res = await fetch("/api/shelf-monitoring/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Upload failed (${res.status})`);
      const data = await res.json();

      currentAnalysisId = data.analysis_id;
      analyzeBtn.disabled = false;
      setStatus("ready", `"${selectedFile.name}" uploaded — ready to analyze.`);
    } catch (err) {
      console.error(err);
      uploadImageBtn.disabled = false;
      setStatus("selected", "Upload failed. Please try again.");
    }
  });

  // -----------------------------------------------------------
  // Analyze Shelf -> POST /api/shelf-monitoring/analyze/{id}
  // -----------------------------------------------------------
  analyzeBtn.addEventListener("click", async () => {
    if (!currentAnalysisId) return;

    analyzeBtn.disabled = true;
    uploadImageBtn.disabled = true;
    progressWrap.hidden = false;
    progressFill.style.width = "0%";
    progressText.textContent = "Running AI detection model…";
    setStatus("ready", "Analyzing shelf image…");

    requestAnimationFrame(() => { progressFill.style.width = "80%"; });

    try {
      const res = await fetch(`/api/shelf-monitoring/analyze/${currentAnalysisId}`, {
        method: "POST",
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail || `Analysis failed (${res.status})`);
      }

      const data = await res.json();
      progressFill.style.width = "100%";
      progressText.textContent = "Detection complete.";
      setStatus("done", "Analysis complete — results ready below.");
      showResults(data);
      refreshRecentAnalyses();
    } catch (err) {
      console.error(err);
      progressText.textContent = "Detection failed.";
      setStatus("selected", err.message || "Analysis failed. Please try again.");
      analyzeBtn.disabled = false;
      uploadImageBtn.disabled = false;
    }
  });

  // -----------------------------------------------------------
  // Reset
  // -----------------------------------------------------------
  resetBtn.addEventListener("click", resetUI);

  // -----------------------------------------------------------
  // Render: bounding boxes on the detection image
  // -----------------------------------------------------------
  function renderBoundingBoxes(boxes) {
    bboxLayer.innerHTML = "";
    (boxes || []).forEach((box) => {
      const el = document.createElement("div");
      el.className = "bbox" + (box.is_empty ? " is-empty" : "");
      el.style.left = box.x + "%";
      el.style.top = box.y + "%";
      el.style.width = box.w + "%";
      el.style.height = box.h + "%";

      const label = document.createElement("span");
      label.className = "bbox-label";
      label.textContent = box.label;
      el.appendChild(label);

      bboxLayer.appendChild(el);
    });
  }

  // -----------------------------------------------------------
  // Render: per-category detection table
  // -----------------------------------------------------------
  function renderDetectionTable(categoryBreakdown) {
    detectionTableBody.innerHTML = "";
    (categoryBreakdown || []).forEach((row, i) => {
      const tr = document.createElement("tr");
      const dot = BAR_PALETTE[i % BAR_PALETTE.length];
      tr.innerHTML = `
        <td><span class="category-dot" style="--dot:${dot}"></span>${row.category}</td>
        <td>${row.count}</td>
        <td>${row.avg_confidence}%</td>
        <td>${row.shelf_location || "—"}</td>
      `;
      detectionTableBody.appendChild(tr);
    });
  }

  // -----------------------------------------------------------
  // Render: distribution bar chart (all store categories, 0-filled)
  // -----------------------------------------------------------
  function renderBarChart(distribution) {
    barChartBars.innerHTML = "";
    const maxCount = Math.max(1, ...(distribution || []).map((c) => c.count));

    (distribution || []).forEach((cat, i) => {
      const heightPct = Math.max(4, Math.round((cat.count / maxCount) * 100));
      const color = BAR_PALETTE[i % BAR_PALETTE.length];
      const item = document.createElement("div");
      item.className = "bar-item";
      item.innerHTML = `
        <span class="bar-fill" style="--h:${heightPct}%; --c:${color}"></span>
        <span class="bar-value">${cat.count}</span>
        <span class="bar-label">${cat.category}</span>
      `;
      barChartBars.appendChild(item);
    });
  }

  // -----------------------------------------------------------
  // Render: detection statistics section
  // -----------------------------------------------------------
  function renderStats(data) {
    statMostDetected.textContent = data.most_detected_category || "—";
    statLeastDetected.textContent = data.least_detected_category || "—";
    statEmptySections.textContent = `${data.empty_spaces} section${data.empty_spaces === 1 ? "" : "s"}`;
    statTotalCapacity.textContent = `${data.total_shelf_capacity} slots`;
    statProcessingTime.textContent = data.processing_time_ms != null
      ? `${(data.processing_time_ms / 1000).toFixed(1)}s`
      : "—";
  }

  // -----------------------------------------------------------
  // Render: AI-generated insights
  // -----------------------------------------------------------
  function renderInsights(insights) {
    insightsGrid.innerHTML = "";
    if (!insights || !insights.length) {
      insightsGrid.innerHTML = `<div class="insight-card"><span class="insight-icon">ℹ️</span><p>No insights available for this analysis.</p></div>`;
      return;
    }
    insights.forEach((ins) => {
      const card = document.createElement("div");
      card.className = "insight-card";
      card.innerHTML = `<span class="insight-icon">${ins.icon}</span><p>${ins.text}</p>`;
      insightsGrid.appendChild(card);
    });
  }

  // -----------------------------------------------------------
  // Reveal results using the real API response
  // -----------------------------------------------------------
  function showResults(data) {
    originalImageEl.src = data.original_image_url || objectUrl;
    detectionImageEl.src = data.detection_image_url || data.original_image_url || objectUrl;

    renderBoundingBoxes(data.boxes);
    renderDetectionTable(data.category_breakdown);
    renderBarChart(data.full_category_distribution);
    renderStats(data);
    renderInsights(data.insights);

    if (kpiTotalProducts) kpiTotalProducts.textContent = data.total_products;
    if (kpiEmptySpaces) kpiEmptySpaces.textContent = data.empty_spaces;
    if (kpiOccupancy) kpiOccupancy.textContent = `${data.occupancy_percentage}%`;
    if (kpiClasses) kpiClasses.textContent = data.classes_detected;
    if (kpiConfidence) kpiConfidence.textContent = `${data.avg_confidence}%`;

    const occupiedPct = Math.round(data.occupancy_percentage);
    const emptyPct = 100 - occupiedPct;
    doughnutChart.style.setProperty("--pct", "0");
    doughnutPct.textContent = "0%";
    window.setTimeout(() => {
      doughnutChart.style.setProperty("--pct", String(occupiedPct));
      doughnutPct.textContent = occupiedPct + "%";
      if (legendOccupiedPct) legendOccupiedPct.textContent = `${occupiedPct}%`;
      if (legendEmptyPct) legendEmptyPct.textContent = `${emptyPct}%`;
    }, 80);

    const now = new Date(data.created_at || Date.now());
    lastAnalysisTimeEl.textContent = now.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }) + ", " + now.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });

    resultsWrapper.hidden = false;
    resultsWrapper.scrollIntoView({ behavior: "smooth", block: "start" });

    uploadImageBtn.disabled = false;
    analyzeBtn.disabled = false;
    currentAnalysisId = data.analysis_id || currentAnalysisId;
  }

  // -----------------------------------------------------------
  // Recent analyses: fetch + render + "View Result" wiring
  // -----------------------------------------------------------
  async function refreshRecentAnalyses() {
    try {
      const res = await fetch("/api/shelf-monitoring/recent");
      if (!res.ok) return;
      const data = await res.json();
      renderRecentAnalyses(data.items);
    } catch (err) {
      console.error("Failed to refresh recent analyses", err);
    }
  }

  function renderRecentAnalyses(items) {
    if (!recentAnalysesBody) return;
    if (!items || !items.length) {
      recentAnalysesBody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No analyses yet — upload a shelf image to get started.</td></tr>`;
      return;
    }

    recentAnalysesBody.innerHTML = "";
    items.forEach((a) => {
      const statusClass = a.status === "completed" ? "status-ready" : a.status === "failed" ? "status-failed" : "status-pending";
      const statusLabel = a.status === "completed" ? "Completed" : a.status === "failed" ? "Failed" : "Processing";
      const disabledAttr = a.status === "completed" ? "" : "disabled";
      const dateLabel = new Date(a.created_at).toLocaleString("en-US", {
        month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit",
      });

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${a.analysis_id}</td>
        <td>${dateLabel}</td>
        <td>${a.uploaded_by_name}</td>
        <td>${a.total_products ?? "—"}</td>
        <td>${a.empty_spaces ?? "—"}</td>
        <td><span class="status-pill ${statusClass}">${statusLabel}</span></td>
        <td><button class="view-result-btn" data-analysis-id="${a.analysis_id}" ${disabledAttr}>View Result</button></td>
      `;
      recentAnalysesBody.appendChild(tr);
    });

    attachViewResultHandlers();
  }

  function attachViewResultHandlers() {
    document.querySelectorAll(".view-result-btn").forEach((btn) => {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "true";
      btn.addEventListener("click", async () => {
        const id = btn.dataset.analysisId;
        if (!id) return;
        try {
          const res = await fetch(`/api/shelf-monitoring/${id}`);
          if (!res.ok) throw new Error("Could not load that analysis result.");
          const data = await res.json();
          showResults(data);
        } catch (err) {
          console.error(err);
          alert(err.message || "Could not load that analysis result.");
        }
      });
    });
  }

  // -----------------------------------------------------------
  // Quick actions
  // -----------------------------------------------------------
  const qaUploadNew = document.getElementById("qaUploadNew");
  const qaRunAgain = document.getElementById("qaRunAgain");
  const qaDownloadResult = document.getElementById("qaDownloadResult");
  const qaExportReport = document.getElementById("qaExportReport");

  if (qaUploadNew) {
    qaUploadNew.addEventListener("click", () => {
      resetUI();
      dropzone.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  if (qaRunAgain) {
    qaRunAgain.addEventListener("click", () => {
      if (!currentAnalysisId) {
        dropzone.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }
      analyzeBtn.click();
    });
  }

  if (qaDownloadResult) {
    qaDownloadResult.addEventListener("click", () => {
      if (!currentAnalysisId) return;
      window.location.href = `/api/shelf-monitoring/${currentAnalysisId}/download-result`;
    });
  }

  if (qaExportReport) {
    qaExportReport.addEventListener("click", () => {
      // BACKEND INTEGRATION POINT (pending ai_modules/report_generator):
      // window.location.href = `/api/shelf-monitoring/${currentAnalysisId}/export-report`;
      alert("Export will generate a PDF detection report once the report generator module is built.");
    });
  }

  // Initial state
  attachViewResultHandlers(); // binds any server-rendered "View Result" rows
  resetUI();
})();