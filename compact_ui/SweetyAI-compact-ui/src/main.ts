import "./styles.css";

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

const API_URL = "http://127.0.0.1:8765/chat";

const logoWrapper = document.getElementById("coucou-logo-wrapper") as HTMLDivElement;
const sweetyLogo = document.getElementById("sweety-logo") as HTMLDivElement;
const sweetyEyes = document.querySelectorAll<HTMLElement>(".sweety-eye");
const chatbox = document.getElementById("sweety-chatbox") as HTMLDivElement;
const chatMessages = document.getElementById("chat-messages") as HTMLDivElement;
const chatInput = document.getElementById("chat-input") as HTMLInputElement;
const sendBtn = document.getElementById("send-btn") as HTMLButtonElement;

const messages: ChatMessage[] = [];
let busy = false;
let currentHue = 0;

function appendMessage(text: string, className: "msg-user" | "msg-ai") {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${className}`;
  msgDiv.textContent = text;
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setBusy(value: boolean) {
  busy = value;
  sendBtn.disabled = value;
  chatInput.disabled = value;
  sendBtn.textContent = value ? "..." : "Send";
}

async function sendMessage() {
  if (busy) return;

  const text = chatInput.value.trim();
  if (!text) return;

  messages.push({ role: "user", content: text });
  appendMessage(text, "msg-user");
  chatInput.value = "";
  setBusy(true);

  sweetyLogo.classList.add("is-blinking");
  setTimeout(() => sweetyLogo.classList.remove("is-blinking"), 150);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.ok) {
      throw new Error(data?.error || `HTTP ${response.status}`);
    }

    const reply = String(data.content ?? "");
    messages.push({ role: "assistant", content: reply });
    appendMessage(reply, "msg-ai");
  } catch (error) {
    const reply = `Backend connection error: ${error instanceof Error ? error.message : String(error)}`;
    messages.push({ role: "system", content: reply });
    appendMessage(reply, "msg-ai");
  } finally {
    setBusy(false);
    chatInput.focus();
  }
}

logoWrapper.addEventListener("click", () => {
  chatbox.classList.toggle("active");
  if (chatbox.classList.contains("active")) {
    chatInput.focus();
  }
});

sendBtn.addEventListener("click", () => void sendMessage());

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    void sendMessage();
  }
});

setInterval(() => {
  if (busy) return;
  currentHue = (currentHue + 60) % 360;
  document.documentElement.style.setProperty(
    "--sweety-color",
    `hsl(${currentHue}, 80%, 75%)`,
  );
}, 20000);

let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let currentX = 0;
let currentY = 0;

document.addEventListener("mousemove", (event) => {
  mouseX = event.clientX;
  mouseY = event.clientY;
});

function triggerBlink() {
  sweetyLogo.classList.add("is-blinking");
  setTimeout(() => sweetyLogo.classList.remove("is-blinking"), 120);
  setTimeout(triggerBlink, Math.random() * 4000 + 2000);
}

setTimeout(triggerBlink, 2000);

function renderSweety() {
  const rect = logoWrapper.getBoundingClientRect();
  const logoCenterX = rect.left + rect.width / 2;
  const logoCenterY = rect.top + rect.height / 2;

  let targetOffsetX = (mouseX - logoCenterX) / (window.innerWidth / 1.5);
  let targetOffsetY = (mouseY - logoCenterY) / (window.innerHeight / 1.5);

  targetOffsetX = Math.max(-1, Math.min(1, targetOffsetX));
  targetOffsetY = Math.max(-1, Math.min(1, targetOffsetY));

  currentX += (targetOffsetX - currentX) * 0.1;
  currentY += (targetOffsetY - currentY) * 0.1;

  const rotateY = currentX * 15;
  const rotateX = -currentY * 15;
  sweetyLogo.style.transform = `perspective(400px) rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;

  sweetyEyes.forEach((eye) => {
    eye.style.transform = `translate(${currentX * 6}px, ${currentY * 6}px)`;
  });

  requestAnimationFrame(renderSweety);
}

renderSweety();
