/* ==========================================================
   RetailIQ — Customer Main Page Client-Side Interactions
   ========================================================== */

// Store opening hours used to compute Open / Closed status.
const STORE_HOURS = { openHour: 9, closeHour: 23 };

// Elements
const greetingWordEl = document.getElementById("greetingWord");
const currentDateEl = document.getElementById("currentDate");
const currentTimeEl = document.getElementById("currentTime");
const storeStatusTextEl = document.getElementById("storeStatusText");
const storeStatusPillEl = document.getElementById("storeStatusPill");
const infoStoreStatusEl = document.getElementById("infoStoreStatus");

// Dropdown Elements
const userMenuWrapper = document.querySelector(".user-menu");
const userMenuTrigger = document.querySelector(".user-menu-trigger");

function greetingForHour(hour) {
  if (hour < 12) return "Good Morning";
  if (hour < 18) return "Good Afternoon";
  return "Good Evening";
}

function updateLiveClockAndStatus() {
  const now = new Date();
  
  // Format Date
  const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  if (currentDateEl) currentDateEl.textContent = now.toLocaleDateString('en-US', dateOptions);
  
  // Format Time
  let hours = now.getHours();
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // Convert 0 to 12
  if (currentTimeEl) currentTimeEl.textContent = `${hours}:${minutes} ${ampm}`;
  
  // Dynamic Greeting
  const currentHour = now.getHours();
  if (greetingWordEl) greetingWordEl.textContent = greetingForHour(currentHour);
  
  // Compute Retail Store Status
  if (currentHour >= STORE_HOURS.openHour && currentHour < STORE_HOURS.closeHour) {
    if (storeStatusPillEl) storeStatusPillEl.className = "status-pill is-open";
    if (storeStatusTextEl) storeStatusTextEl.textContent = "Operational";
    if (infoStoreStatusEl) infoStoreStatusEl.innerHTML = `<strong>Open:</strong> Stores closing at ${STORE_HOURS.closeHour % 12} PM`;
  } else {
    if (storeStatusPillEl) storeStatusPillEl.className = "status-pill is-closed";
    if (storeStatusTextEl) storeStatusTextEl.textContent = "Closed";
    if (infoStoreStatusEl) infoStoreStatusEl.innerHTML = `<strong>Closed:</strong> Opens tomorrow at ${STORE_HOURS.openHour} AM`;
  }
}

// -----------------------------------------------------------
// Action: Dropdown Menu Trigger Handler
// -----------------------------------------------------------
if (userMenuTrigger && userMenuWrapper) {
  userMenuTrigger.addEventListener("click", (e) => {
    e.stopPropagation(); // Prevents instant document listener trigger
    userMenuWrapper.classList.toggle("is-open");
  });
}

// Click anywhere else on the screen window to auto-minimize dropdown safely
document.addEventListener("click", () => {
  if (userMenuWrapper && userMenuWrapper.classList.contains("is-open")) {
    userMenuWrapper.classList.remove("is-open");
  }
});

// -----------------------------------------------------------
// Action: Clear Token and Session Cookies on Logout
// -----------------------------------------------------------
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", (e) => {
    e.preventDefault();
    
    // Clear tokens stored locally
    localStorage.clear();
    
    // Clear cookie authorization token string by forcing an expired timestamp
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    
    // Redirect cleanly to the root Home Landing Page
    window.location.href = "/";
  });
}

// Favorite state toggler placeholder logic
document.querySelectorAll(".favorite-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    btn.classList.toggle("is-active");
  });
});

document.querySelectorAll(".product-view-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const card = btn.closest(".product-card");
    console.log("View details for product ID:", card?.dataset.id);
  });
});

// -----------------------------------------------------------
// Smart tips rotator
// -----------------------------------------------------------
const SMART_TIPS = [
  "Check today's offers before shopping.",
  "Ask the AI Assistant for product recommendations.",
  "View your spending insights on the Dashboard.",
  "Explore new arrivals in your favorite categories.",
];

const tipTextEl = document.getElementById("tipText");
const tipDotsEl = document.getElementById("tipDots");
let tipIndex = 0;

function renderTipDots() {
  if (!tipDotsEl) return;
  tipDotsEl.innerHTML = "";
  SMART_TIPS.forEach((_, i) => {
    const dot = document.createElement("span");
    dot.className = "tip-dot" + (i === tipIndex ? " is-active" : "");
    dot.addEventListener("click", () => showTip(i));
    tipDotsEl.appendChild(dot);
  });
}

function showTip(index) {
  if (!tipTextEl) return;
  tipIndex = index;
  tipTextEl.style.opacity = 0;
  window.setTimeout(() => {
    tipTextEl.textContent = SMART_TIPS[tipIndex];
    tipTextEl.style.opacity = 1;
    renderTipDots();
  }, 300);
}

// -----------------------------------------------------------
// Real-Time Countdown engine for Offers
// -----------------------------------------------------------
function initializeOfferCountdowns() {
  const countdownElements = document.querySelectorAll(".live-countdown");

  function updateTimers() {
    const now = new Date();

    countdownElements.forEach((el) => {
      const expiresAttr = el.getAttribute("data-expires");
      if (!expiresAttr) {
        el.textContent = "Limited Time";
        return;
      }

      const expiryDate = new Date(expiresAttr);
      const diffMs = expiryDate - now;

      if (diffMs <= 0) {
        el.textContent = "Expired";
        el.style.color = "red";
        return;
      }

      // Math conversions
      const totalSeconds = Math.floor(diffMs / 1000);
      const days = Math.floor(totalSeconds / 86400);
      const hours = Math.floor((totalSeconds % 86400) / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);

      if (days > 0) {
        el.textContent = `Ends in ${days}d ${hours}h`;
      } else if (hours > 0) {
        el.textContent = `Ends in ${hours}h ${minutes}m`;
      } else {
        el.textContent = `Ends in ${minutes}m`;
      }
    });
  }

  updateTimers();
  window.setInterval(updateTimers, 60000); // Check once a minute to preserve client CPU 
}

// -----------------------------------------------------------
// Initializer Sequence Execution
// -----------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  updateLiveClockAndStatus();
  window.setInterval(updateLiveClockAndStatus, 30000);
  
  initializeOfferCountdowns(); // <--- This activates the database countdowns
  
  showTip(0);
  window.setInterval(() => {
    let next = (tipIndex + 1) % SMART_TIPS.length;
    showTip(next);
  }, 6000);
});