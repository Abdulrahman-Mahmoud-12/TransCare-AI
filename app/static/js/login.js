/* ==========================================================
   RetailIQ — Login page interactions + auth API wiring
   ========================================================== */

const API_CONFIG = {
  BASE_URL: window.location.origin, 
  ENDPOINT: "/auth/login",
};

// Application view layer landing locations 
const ROLE_REDIRECTS = {
  customer: "/customer/main",
  admin: "/admin/main",
};

// Elements
const form = document.getElementById("loginForm");
const emailInput = document.getElementById("loginEmail");
const passwordInput = document.getElementById("loginPassword");
const rememberInput = document.getElementById("rememberMe");
const submitBtn = document.getElementById("loginSubmit");
const statusEl = document.getElementById("loginStatus");
const toggleBtn = document.getElementById("togglePassword");
const roleTabs = Array.from(document.querySelectorAll(".auth-tab"));

let activeRole = "customer"; // Default state fallback
let isRequesting = false;

// Dynamic Role Switcher tabs
roleTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    if (isRequesting) return;

    roleTabs.forEach((t) => {
      t.classList.remove("is-active");
      t.setAttribute("aria-selected", "false");
    });

    tab.classList.add("is-active");
    tab.setAttribute("aria-selected", "true");

    activeRole = tab.dataset.role;
    clearStatus();
  });
});

// Hide/Show plain text password toggle logic
toggleBtn.addEventListener("click", () => {
  const isPrivate = passwordInput.type === "password";
  passwordInput.type = isPrivate ? "text" : "password";
  toggleBtn.textContent = isPrivate ? "Hide" : "Show";
});

function setStatus(msg, type) {
  statusEl.className = "role-status";
  if (type) statusEl.classList.add(`is-${type}`);
  statusEl.textContent = msg;
  
  // Custom status color assignments
  if (type === "error") {
    statusEl.style.color = "#c8461e";
  } else if (type === "success") {
    statusEl.style.color = "var(--teal-600, #0f9b8e)";
  } else {
    statusEl.style.color = "var(--text-muted)";
  }
}

function clearStatus() {
  statusEl.className = "role-status";
  statusEl.textContent = "";
}

function setLoading(loading) {
  isRequesting = loading;
  submitBtn.disabled = loading;
  const label = submitBtn.querySelector(".auth-submit-label");
  if (label) {
    label.textContent = loading ? "Authenticating Session..." : "Log in";
  }
}

function validate(email, password) {
  if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
    return "Enter a valid email address.";
  }
  if (!password || password.length < 6) {
    return "Password must be at least 6 characters.";
  }
  return null;
}

// Event Dispatcher for Form Submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (isRequesting) return;

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  const validationError = validate(email, password);
  if (validationError) {
    setStatus(validationError, "error");
    return;
  }

  setLoading(true);
  setStatus(`Signing into your ${capitalize(activeRole)} workspace...`, null);

  try {
    const response = await fetch(API_CONFIG.BASE_URL + API_CONFIG.ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Incorrect email or password.");
    }

    // FIXED: Instead of failing, intelligently auto-correct the redirection path 
    // to match the account's actual role from the database.
    localStorage.setItem("user_role", data.role);

    setStatus("Welcome back! Redirecting to workspace...", "success");

    const destination = ROLE_REDIRECTS[data.role] || "/";
    window.setTimeout(() => {
      window.location.href = destination;
    }, 1000);

  } catch (err) {
    console.error("RetailIQ authorization failure:", err);
    setStatus(err.message, "error");
    setLoading(false);
  }
});

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}