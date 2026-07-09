/* ==========================================================
   RetailIQ — Admin Main Page interactions
   ========================================================== */

// Store opening hours used to compute Open / Closed status.
const STORE_HOURS = { openHour: 9, closeHour: 23 };

// -----------------------------------------------------------
// 2. Greeting + live clock (Updated to match customer AM/PM style)
// -----------------------------------------------------------
const greetingWordEl = document.getElementById("greetingWord");
const adminFirstNameEl = document.getElementById("adminFirstName");
const currentDateEl = document.getElementById("currentDate");
const currentTimeEl = document.getElementById("currentTime");
const storeStatusTextEl = document.getElementById("storeStatusText");
const storeStatusPillEl = document.getElementById("storeStatusPill");
const statusCardStoreValueEl = document.getElementById("statusCardStoreValue");
const statusCardStoreDotEl = document.getElementById("statusCardStoreDot");
const profileAvatarInitialEl = document.getElementById("profileAvatarInitial");
const adminNameLabelEl = document.getElementById("adminNameLabel");

function greetingForHour(hour) {
  if (hour < 12) return "Good Morning";
  if (hour < 18) return "Good Afternoon";
  return "Good Evening";
}

function updateClock() {
  const now = new Date();
  const hour = now.getHours();

  if (greetingWordEl) greetingWordEl.textContent = greetingForHour(hour);

  if (currentDateEl) {
    currentDateEl.textContent = now.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  }

  if (currentTimeEl) {
    // EDITED: Formatted to beautiful 12-hour AM/PM clock just like customer-main.js
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; 
    currentTimeEl.textContent = `${hours}:${minutes} ${ampm}`;
  }

  const isOpen = hour >= STORE_HOURS.openHour && hour < STORE_HOURS.closeHour;
  const statusLabel = isOpen ? "🟢 Open" : "🔴 Closed";

  if (storeStatusTextEl) storeStatusTextEl.textContent = statusLabel;
  if (storeStatusPillEl) {
    storeStatusPillEl.classList.toggle("store-open", isOpen);
    storeStatusPillEl.classList.toggle("store-closed", !isOpen);
  }

  if (statusCardStoreValueEl) {
    statusCardStoreValueEl.textContent = isOpen ? "Open" : "Closed";
  }
  if (statusCardStoreDotEl) {
    statusCardStoreDotEl.classList.toggle("dot-green", isOpen);
    statusCardStoreDotEl.classList.toggle("dot-red", !isOpen);
  }
}

updateClock();
setInterval(updateClock, 30000);

// -----------------------------------------------------------
// 3. Dropdown menus (notifications, alerts, profile)
// -----------------------------------------------------------
function setupDropdown(menuEl, triggerEl) {
  if (!menuEl || !triggerEl) return;
  triggerEl.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = menuEl.classList.toggle("is-open");
    triggerEl.setAttribute("aria-expanded", String(isOpen));
    // Close any other open menus.
    document.querySelectorAll(".icon-menu.is-open, .admin-profile.is-open").forEach((el) => {
      if (el !== menuEl) {
        el.classList.remove("is-open");
        const t = el.querySelector("button");
        if (t) t.setAttribute("aria-expanded", "false");
      }
    });
  });
}

setupDropdown(document.getElementById("notifMenu"), document.getElementById("notifBtn"));
setupDropdown(document.getElementById("alertsMenu"), document.getElementById("alertsBtn"));
setupDropdown(document.getElementById("adminProfileMenu"), document.getElementById("profileTrigger"));

document.addEventListener("click", (e) => {
  document.querySelectorAll(".icon-menu.is-open, .admin-profile.is-open").forEach((el) => {
    if (!el.contains(e.target)) {
      el.classList.remove("is-open");
      const t = el.querySelector("button");
      if (t) t.setAttribute("aria-expanded", "false");
    }
  });
});

// -----------------------------------------------------------
// 4. Logout (EDITED: Clears tokens/storage like customer-main.js)
// -----------------------------------------------------------
function handleLogout() {
  localStorage.clear();
  document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  window.location.href = "/";
}

const logoutBtn = document.getElementById("logoutBtn");
const sidebarLogoutBtn = document.getElementById("sidebarLogoutBtn");
if (logoutBtn) logoutBtn.addEventListener("click", handleLogout);
if (sidebarLogoutBtn) sidebarLogoutBtn.addEventListener("click", handleLogout);

// -----------------------------------------------------------
// 5. Sidebar toggle (mobile / small screens)
// -----------------------------------------------------------
const sidebarToggle = document.getElementById("sidebarToggle");
const adminSidebar = document.getElementById("adminSidebar");

if (sidebarToggle && adminSidebar) {
  sidebarToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    adminSidebar.classList.toggle("is-open");
  });

  document.addEventListener("click", (e) => {
    if (
      adminSidebar.classList.contains("is-open") &&
      !adminSidebar.contains(e.target) &&
      e.target !== sidebarToggle
    ) {
      adminSidebar.classList.remove("is-open");
    }
  });
}

// -----------------------------------------------------------
// 6. Critical Alerts (EDITED: Completely removed static renderAlerts() loops)
// -----------------------------------------------------------
// The static mock arrays are deleted. Alerts are now handled securely on the 
// server side through database queries and populated instantly via the template engine.

// -----------------------------------------------------------
// 7. Business tips rotator
// -----------------------------------------------------------
const BUSINESS_TIPS = [
  "Restock Dairy products before tomorrow.",
  "Beverage sales are increasing this week.",
  "Consider extending today's promotion.",
  "Bakery demand is expected to rise this weekend.",
  "Shelf occupancy in Aisle 3 has dropped below 80%.",
];

const tipTextEl = document.getElementById("tipText");
const tipDotsEl = document.getElementById("tipDots");
let tipIndex = 0;

function renderTipDots() {
  if (!tipDotsEl) return;
  tipDotsEl.innerHTML = "";
  BUSINESS_TIPS.forEach((_, i) => {
    const dot = document.createElement("span");
    dot.className = "tip-dot" + (i === tipIndex ? " is-active" : "");
    tipDotsEl.appendChild(dot);
  });
}

function showTip(index) {
  tipIndex = index;
  if (!tipTextEl) return;
  tipTextEl.style.opacity = 0;
  window.setTimeout(() => {
    tipTextEl.textContent = BUSINESS_TIPS[tipIndex];
    tipTextEl.style.opacity = 1;
    renderTipDots();
  }, 180);
}

if (tipTextEl) {
  tipTextEl.style.transition = "opacity 0.18s ease";
  renderTipDots();

  setInterval(() => {
    const nextIndex = (tipIndex + 1) % BUSINESS_TIPS.length;
    showTip(nextIndex);
  }, 6000);
}