/* ==========================================================
   RetailIQ — Home page interactions + auth API wiring
   ========================================================== */

// -----------------------------------------------------------
// 1. Configuration
// -----------------------------------------------------------
// Point these at your real backend FastAPI endpoints.
// To resolve 404 errors, these point directly to your unified 
// authentication router paths.
const API_CONFIG = {
  BASE_URL: window.location.origin,
  LOGIN_ENDPOINT: "/auth/login"
};

// Where each role should land after a successful sign-in.
const ROLE_REDIRECTS = {
  customer: "/customer/main",
  admin: "/admin/main",
};

// -----------------------------------------------------------
// 2. Auth request
// -----------------------------------------------------------
async function requestSession(role) {
  const url = API_CONFIG.BASE_URL + API_CONFIG.LOGIN_ENDPOINT;

  // The login schema requires email and password. 
  // For immediate landing page role shortcuts, you will usually redirect 
  // straight to the login forms, or supply mock session credentials if intended.
  // Below we dispatch to the unified /auth/login handler.
  const payload = {
    role: role, // "customer" | "admin"
    email: "",  // Homepage quick-actions prompt form redirect or default entry
    password: "",
    source: "homepage",
    timestamp: new Date().toISOString(),
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await safeReadError(response);
    throw new Error(detail || `Sign-in failed (${response.status})`);
  }

  return response.json(); // expected: { access_token, token_type, role }
}

async function safeReadError(response) {
  try {
    const data = await response.json();
    return data.detail || data.message || data.error || null;
  } catch (_) {
    return null;
  }
}

// -----------------------------------------------------------
// 3. Role picker UI
// -----------------------------------------------------------
const overlay = document.getElementById("roleOverlay");
const closeBtn = document.getElementById("roleClose");
const statusEl = document.getElementById("roleStatus");
const roleCards = Array.from(document.querySelectorAll(".role-card"));
const openTriggers = document.querySelectorAll("[data-open-role-picker]");

let isRequesting = false;

function openPicker() {
  overlay.classList.add("is-open");
  overlay.setAttribute("aria-hidden", "false");
  setStatus("", null);
  roleCards.forEach((c) => c.classList.remove("is-selected"));
  document.body.style.overflow = "hidden";
}

function closePicker() {
  if (isRequesting) return;
  overlay.classList.remove("is-open");
  overlay.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function setStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.classList.remove("is-error", "is-success");
  if (kind) statusEl.classList.add(kind === "error" ? "is-error" : "is-success");
}

if (openTriggers.length > 0) openTriggers.forEach((btn) => btn.addEventListener("click", openPicker));
if (closeBtn) closeBtn.addEventListener("click", closePicker);

if (overlay) {
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closePicker();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("is-open")) closePicker();
  });

  overlay.addEventListener("transitionend", () => {
    if (overlay.classList.contains("is-open") && roleCards[0]) {
      roleCards[0].focus();
    }
  });
}

roleCards.forEach((card) => {
  card.addEventListener("click", async () => {
    if (isRequesting) return;

    const role = card.dataset.role;
    roleCards.forEach((c) => c.classList.remove("is-selected"));
    card.classList.add("is-selected");

    // Seamless UX alternative: If clicking a quick role option on the home screen
    // requires a password check, redirect them directly to the detailed login page
    // with their pre-selected role choice!
    window.location.href = `/auth/login?role=${role}`;
  });
});

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}