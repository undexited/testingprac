const state = {
  token: localStorage.getItem("v2_token") || "",
  conversationId: null
};

const api = async (path, opts = {}) => {
  const headers = opts.headers || {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (!headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const res = await fetch(path, { ...opts, headers });
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
};

const statusEl = document.getElementById("status");
const emailEl = document.getElementById("email");
const nameEl = document.getElementById("name");
const passEl = document.getElementById("password");
const modeEl = document.getElementById("mode");
const providerEl = document.getElementById("provider");
const messagesEl = document.getElementById("messages");
const promptEl = document.getElementById("prompt");

function addMsg(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatus(text) {
  statusEl.textContent = text;
}

async function loadMe() {
  if (!state.token) return setStatus("Not logged in");
  try {
    const me = await api("/api/me", { method: "GET", headers: {} });
    setStatus(`Logged in: ${me.display_name} (${me.email})`);
  } catch {
    setStatus("Token invalid, log in again");
    state.token = "";
    localStorage.removeItem("v2_token");
  }
}

document.getElementById("registerBtn").onclick = async () => {
  try {
    const data = await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: emailEl.value.trim(),
        password: passEl.value,
        display_name: nameEl.value.trim() || "User"
      })
    });
    state.token = data.access_token;
    localStorage.setItem("v2_token", state.token);
    await loadMe();
  } catch (e) {
    setStatus(`Register failed: ${e.message}`);
  }
};

document.getElementById("loginBtn").onclick = async () => {
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: emailEl.value.trim(), password: passEl.value })
    });
    state.token = data.access_token;
    localStorage.setItem("v2_token", state.token);
    await loadMe();
  } catch (e) {
    setStatus(`Login failed: ${e.message}`);
  }
};

document.getElementById("newChatBtn").onclick = () => {
  state.conversationId = null;
  messagesEl.innerHTML = "";
  addMsg("ai", "New conversation started.");
};

document.getElementById("sendForm").onsubmit = async (e) => {
  e.preventDefault();
  const prompt = promptEl.value.trim();
  if (!prompt) return;
  if (!state.token) return setStatus("Please log in first.");

  addMsg("user", prompt);
  promptEl.value = "";
  setStatus("Sending...");

  try {
    const data = await api("/api/chat/send", {
      method: "POST",
      body: JSON.stringify({
        message: prompt,
        mode: modeEl.value,
        provider: providerEl.value || null,
        conversation_id: state.conversationId
      })
    });
    state.conversationId = data.conversation_id;
    addMsg("ai", data.assistant_message.content);
    setStatus(`Ready • ${data.assistant_message.provider}/${data.assistant_message.model} • ${data.assistant_message.latency_ms}ms`);
  } catch (e2) {
    addMsg("ai", `Error: ${e2.message}`);
    setStatus("Request failed");
  }
};

addMsg("ai", "Welcome to TestingPrac AI v2. Register or log in to begin.");
loadMe();
