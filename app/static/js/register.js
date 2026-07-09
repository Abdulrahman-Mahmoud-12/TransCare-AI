/* ==========================================================
   RetailIQ — Register page interactions + auth API wiring
   ========================================================== */
const API_CONFIG = {
  BASE_URL: window.location.origin, 
  CUSTOMER_ENDPOINT: "/auth/register",
  ADMIN_ENDPOINT: "/auth/register",
};

const ROLE_REDIRECTS = {
  customer: "/customer/main",
  admin: "/admin/main", 
};

function endpointForRole(role) {
  return API_CONFIG.BASE_URL + API_CONFIG.CUSTOMER_ENDPOINT;
}

// Elements
const form = document.getElementById("registerForm");
const nameInput = document.getElementById("registerName");
const emailInput = document.getElementById("registerEmail");
const orgField = document.getElementById("orgField");
const orgInput = document.getElementById("registerOrg");
const passwordInput = document.getElementById("registerPassword");
const confirmInput = document.getElementById("registerConfirm");
const termsInput = document.getElementById("agreeTerms");
const submitBtn = document.getElementById("registerSubmit");
const statusEl = document.getElementById("registerStatus");
const toggleBtn = document.getElementById("togglePassword");
const roleTabs = Array.from(document.querySelectorAll(".auth-role-tab"));

// Secure admin passcode DOM nodes
const adminVerificationField = document.getElementById("adminVerificationField");
const adminIdInput = document.getElementById("registerAdminId");

let activeRole = "customer";
let isRequesting = false;

// Tab Switcher Logic
roleTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    if (isRequesting) return;

    roleTabs.forEach((t) => {
      t.classList.remove("is-active");
      t.setAttribute("aria-selected", "false");
    });

    tab.classList.add("is-active");
    tab.setAttribute("aria-selected", "true");

    activeRole = tab.dataset.role; // This will correctly capture "customer" or "admin"
    clearStatus();

    // FIXED: Match against "admin" data-role value from HTML
    if (activeRole === "admin") {
      orgField.style.display = "block";
      adminVerificationField.style.display = "block"; // Instantly displays the admin key field container
      orgInput.setAttribute("required", "true");
      adminIdInput.setAttribute("required", "true");
    } else {
      orgField.style.display = "none";
      adminVerificationField.style.display = "none"; // Hides it for regular customers
      orgInput.removeAttribute("required");
      adminIdInput.removeAttribute("required");
    }
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
    label.textContent = loading ? "Verifying Credentials..." : "Create account";
  }
}

function validate(payload, role) {
  if (!payload.fullName || payload.fullName.length < 3) {
    return "Name must be at least 3 characters long.";
  }
  if (!payload.email || !/^\S+@\S+\.\S+$/.test(payload.email)) {
    return "Please enter a valid email address.";
  }
  if (role === "admin" && !payload.orgName) {
    return "Organization name is required for Managers/Owners.";
  }
  if (role === "admin" && !payload.adminId) {
    return "Admin Passcode Key token validation is mandatory.";
  }
  if (!payload.password || payload.password.length < 8) {
    return "Password must be at least 8 characters long.";
  }
  if (payload.password !== payload.confirmPassword) {
    return "Passwords do not match.";
  }
  if (!payload.agreedToTerms) {
    return "Please agree to the Terms of Service and Privacy Policy.";
  }
  return null;
}

async function requestRegister(role, payload) {
  const url = endpointForRole(role);

  // Match the exact field names expected by your FastAPI Pydantic schema
  const bodyData = {
    full_name: payload.fullName,
    email: payload.email,
    password: payload.password,
    role: role,
    admin_id: role === "admin" ? payload.adminId : null
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyData),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Registration failed.");
  }
  return data;
}

// Form Submission Event Listener
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (isRequesting) return;

  const formValues = {
    fullName: nameInput.value.trim(),
    email: emailInput.value.trim(),
    orgName: orgInput.value.trim(),
    adminId: adminIdInput.value.trim(), 
    password: passwordInput.value,
    confirmPassword: confirmInput.value,
    agreedToTerms: termsInput.checked,
  };

  const validationError = validate(formValues, activeRole);
  if (validationError) {
    setStatus(validationError, "error");
    return;
  }

  setLoading(true);
  setStatus(`Creating your ${capitalize(activeRole)} account…`, null);

  try {
    await requestRegister(activeRole, formValues);
    setStatus("Account verified and created successfully! Redirecting to log in...", "success");

    window.setTimeout(() => {
      window.location.href = "/auth/login";
    }, 1200);
  } catch (err) {
    console.error("RetailIQ registration error:", err);
    setStatus(err.message || "We couldn't create your account. Please try again.", "error");
    setLoading(false);
  }
});

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
} 