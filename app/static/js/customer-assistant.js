/* ==========================================================
   RetailIQ — Customer AI Assistant Page Client-Side Interactions
   ========================================================== */

// -----------------------------------------------------------
// Elements
// -----------------------------------------------------------
const chatMessagesEl = document.getElementById("chatMessages");
const chatEmptyStateEl = document.getElementById("chatEmptyState");
const chatSuggestionsEl = document.getElementById("chatSuggestions");
const emptyStateSuggestionsEl = document.getElementById("emptyStateSuggestions");
const chatInputEl = document.getElementById("chatInput");
const sendBtnEl = document.getElementById("sendBtn");
const micBtnEl = document.getElementById("micBtn");
const clearChatBtnEl = document.getElementById("clearChatBtn");
const recentConvoListEl = document.getElementById("recentConvoList");
const aiStatusPillEl = document.getElementById("aiStatusPill");
const aiStatusTextEl = document.getElementById("aiStatusText");

const userInitialEl = document.getElementById("userAvatarInitial");
const CUSTOMER_INITIAL = userInitialEl ? userInitialEl.textContent.trim() : "C";

// -----------------------------------------------------------
// State Management (Cleaned History)
// -----------------------------------------------------------
let messages = [];
let messageCounter = 0;
let isAiTyping = false;

// Only the top 3 most important questions
const SUGGESTED_QUESTIONS = [
  "What offers are available today?",
  "What is the best products in range 100 EGP?",
  "What time does the store close?"
];

// Completely clear the historical list
const RECENT_CONVERSATIONS = [];

// -----------------------------------------------------------
// Format Time Helper
// -----------------------------------------------------------
function formatTime() {
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12; 
  return `${hours}:${minutes} ${ampm}`;
}

// -----------------------------------------------------------
// Render Suggestion Chips
// -----------------------------------------------------------
function renderSuggestionChips(containerEl) {
  if (!containerEl) return;
  containerEl.innerHTML = "";

  SUGGESTED_QUESTIONS.forEach((question) => {
    const chip = document.createElement("button");
    chip.className = "suggestion-chip";
    chip.textContent = question;
    
    // Quick action functionality: Click submits immediately
    chip.addEventListener("click", () => {
      submitQuickAction(question);
    });
    
    containerEl.appendChild(chip);
  });
}

// -----------------------------------------------------------
// Render Recent Conversations
// -----------------------------------------------------------
function renderRecentConversations() {
  if (!recentConvoListEl) return;
  recentConvoListEl.innerHTML = "";

  if (RECENT_CONVERSATIONS.length === 0) {
    recentConvoListEl.innerHTML = `<p class="empty-recent">No recent chats</p>`;
    return;
  }

  RECENT_CONVERSATIONS.forEach((convo) => {
    const item = document.createElement("div");
    item.className = "recent-convo-item";
    item.innerHTML = `
      <span class="recent-convo-icon">💬</span>
      <div class="recent-convo-info">
        <span class="recent-convo-title">${convo.title}</span>
        <span class="recent-convo-preview">${convo.preview}</span>
      </div>
      <button class="recent-convo-delete" title="Delete chat">&times;</button>
    `;
    recentConvoListEl.appendChild(item);
  });
}

// -----------------------------------------------------------
// Add Message to DOM
// -----------------------------------------------------------
function addMessage({ role, text, data = null }) {
  messageCounter++;
  const id = `msg-${messageCounter}`;
  const timestamp = formatTime();

  if (messages.length === 0 && role === "user") {
    if (chatEmptyStateEl) chatEmptyStateEl.style.display = "none";
  }

  messages.push({ id, role, text, data, timestamp });

  const msgBubble = document.createElement("div");
  msgBubble.className = `message-bubble ${role === "user" ? "user-bubble" : "assistant-bubble"}`;
  
  let avatarMarkup = "";
  if (role === "user") {
    avatarMarkup = `<div class="msg-avatar user-avatar">${CUSTOMER_INITIAL}</div>`;
  } else {
    avatarMarkup = `
      <div class="msg-avatar assistant-avatar">
        <img src="/static/images/logo.png" alt="RetailIQ AI" onerror="this.innerHTML='IQ';this.className='msg-avatar assistant-avatar-fallback';">
      </div>`;
  }

  let contentMarkup = `<div class="msg-text">${text}</div>`;

  // Render Rich Interactive Components dynamically
  if (data && data.kind === "product") {
    contentMarkup += `
      <div class="rich-card product-card">
        <div class="rich-card-header">
          <span class="rich-card-emoji">${data.emoji || "📦"}</span>
          <div class="rich-card-title-wrap">
            <h4>${data.name}</h4>
            <span class="rich-card-meta">${data.category || "General"}</span>
          </div>
        </div>
        <div class="rich-card-body">
          <div class="product-price">$${data.price.toFixed(2)}</div>
        </div>
      </div>`;
  } else if (data && data.kind === "offer") {
    contentMarkup += `
      <div class="rich-card offer-card">
        <div class="offer-badge">${data.discount}% OFF</div>
        <div class="rich-card-header">
          <span class="rich-card-emoji">${data.emoji || "🏷️"}</span>
          <div class="rich-card-title-wrap">
            <h4>${data.name}</h4>
            <span class="rich-card-meta">Limited Time Promo</span>
          </div>
        </div>
        <div class="rich-card-body">
          <div class="offer-pricing">
            <span class="current-price">$${data.price.toFixed(2)}</span>
          </div>
          <div class="offer-expiry">⏳ Expires in: <strong>${data.endsIn || "Soon"}</strong></div>
        </div>
      </div>`;
  }

  msgBubble.innerHTML = `
    ${role === "assistant" ? avatarMarkup : ""}
    <div class="msg-body-wrapper">
      ${contentMarkup}
      <span class="msg-time">${timestamp}</span>
    </div>
    ${role === "user" ? avatarMarkup : ""}
  `;

  chatMessagesEl.appendChild(msgBubble);
  chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

// -----------------------------------------------------------
// Backend API Connection
// -----------------------------------------------------------
async function handleAiResponse(userText) {
  setAiStatus(true);
  showTypingIndicator();

  try {
    const response = await fetch("/api/customer/assistant/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: userText })
    });

    if (!response.ok) throw new Error("Server communication error");
    
    const reply = await response.json();
    
    hideTypingIndicator();
    setAiStatus(false);
    
    addMessage({ 
      role: "assistant", 
      text: reply.text, 
      data: reply.data 
    });
    
  } catch (error) {
    console.error(error);
    hideTypingIndicator();
    setAiStatus(false);
    
    addMessage({ 
      role: "assistant", 
      text: "I'm having a little trouble checking our store records right now, but I'll be back shortly!" 
    });
  }
}

// -----------------------------------------------------------
// Input Control Actions
// -----------------------------------------------------------
function sendCurrentInput() {
  const text = chatInputEl.value.trim();
  if (!text || isAiTyping) return;

  chatInputEl.value = "";
  autoResizeInput();
  
  addMessage({ role: "user", text: text });
  handleAiResponse(text);
}

function submitQuickAction(textToSubmit) {
  chatInputEl.value = textToSubmit;
  autoResizeInput();
  sendCurrentInput();
}

function setAiStatus(typing) {
  isAiTyping = typing;
  if (typing) {
    aiStatusPillEl.classList.add("status-active");
    aiStatusTextEl.textContent = "AI is thinking...";
    sendBtnEl.disabled = true;
  } else {
    aiStatusPillEl.classList.remove("status-active");
    aiStatusTextEl.textContent = "AI Online";
    sendBtnEl.disabled = false;
  }
}

function showTypingIndicator() {
  const indicator = document.createElement("div");
  indicator.className = "message-bubble assistant-bubble typing-indicator-bubble";
  indicator.id = "typingIndicator";
  indicator.innerHTML = `
    <div class="msg-avatar assistant-avatar"><img src="/static/images/logo.png" alt="AI"></div>
    <div class="msg-body-wrapper">
      <div class="typing-indicator"><span></span><span></span><span></span></div>
    </div>
  `;
  chatMessagesEl.appendChild(indicator);
  chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

function hideTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) indicator.remove();
}

function autoResizeInput() {
  chatInputEl.style.height = "auto";
  chatInputEl.style.height = (chatInputEl.scrollHeight) + "px";
}

// -----------------------------------------------------------
// Initial Greeting Configuration
// -----------------------------------------------------------
function loadInitialConversation() {
  chatMessagesEl.innerHTML = ""; // Clear out everything
  addMessage({
    role: "assistant",
    text: "Hi! I'm your RetailIQ AI Assistant. Ask me about products, prices, offers, or recommendations.",
  });
}

// -----------------------------------------------------------
// Initialize Event Listeners
// -----------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  renderSuggestionChips(chatSuggestionsEl);
  renderSuggestionChips(emptyStateSuggestionsEl);
  renderRecentConversations();
  loadInitialConversation();
  autoResizeInput();

  sendBtnEl.addEventListener("click", sendCurrentInput);
  chatInputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendCurrentInput();
    }
  });

  chatInputEl.addEventListener("input", autoResizeInput);

  if (clearChatBtnEl) {
    clearChatBtnEl.addEventListener("click", () => {
      messages = [];
      loadInitialConversation();
      if (chatEmptyStateEl) chatEmptyStateEl.style.display = "flex";
    });
  }

  // Intercept Quick Actions from assistant.html
  const quickActionButtons = document.querySelectorAll(".quick-action-btn");
  quickActionButtons.forEach((btn) => {
    const actionText = btn.textContent.trim();
    
    if (actionText.includes("Browse Offers")) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        submitQuickAction("What offers are available today?");
      });
    } else if (actionText.includes("Search Products")) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        chatInputEl.value = "Where can I find ";
        autoResizeInput();
        chatInputEl.focus();
      });
    }
  });
});