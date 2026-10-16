
import "./styles.css";
import { getCurrentWindow, LogicalPosition, LogicalSize } from "@tauri-apps/api/window";

type State = "idle" | "menu" | "chat";
type ChatResponse = { ok?: boolean; content?: string; response?: string; error?: string };

const win = getCurrentWindow();
const island = document.getElementById("top-island")!;
const sweetyButton = document.getElementById("sweety-button")!;
const sweetyCore = document.getElementById("sweety-core")!;
const eyes = document.querySelectorAll<HTMLElement>(".eye");
const chatMenu = document.getElementById("chat-menu")!;
const codeMenu = document.getElementById("code-menu")!;
const settingsMenu = document.getElementById("settings-menu")!;
const closeChat = document.getElementById("chat-close");
const chatCard = document.getElementById("chat-card")!;
const composer = document.getElementById("composer") as HTMLFormElement;
const chatInput = document.getElementById("chat-input") as HTMLInputElement;
const sendButton = document.getElementById("send-button") as HTMLButtonElement;
const messages = document.getElementById("chat-messages")!;

const API = "http://127.0.0.1:8765/chat";

async function setTransparentWindowBackground() {
  // The CSS is transparent; keep the native window itself transparent.
  try {
    await win.setIgnoreCursorEvents(false);
  } catch {}
}

function currentState(): State {
  if (island.classList.contains("chat-open")) return "chat";
  if (island.classList.contains("menu-open")) return "menu";
  return "idle";
}

async function setState(state: State) {
  island.classList.remove("menu-open", "chat-open");
  if (state === "menu") island.classList.add("menu-open");
  if (state === "chat") island.classList.add("chat-open");

  // Keep one native transparent stage. The visible content itself changes,
  // avoiding opaque resize artifacts during animation.
  if (state === "chat") {
    setTimeout(() => chatInput.focus(), 220);
  }
}

sweetyButton.addEventListener("click", () => {
  setState(currentState() === "idle" ? "menu" : "idle");
});

chatMenu.addEventListener("click", () => setState("chat"));
codeMenu.addEventListener("click", () => setState("idle"));
settingsMenu.addEventListener("click", () => setState("idle"));

const close = document.getElementById("chat-close")!;
close.addEventListener("click", () => setState("idle"));

function appendBubble(text: string, type: "ai" | "user") {
  const el = document.createElement("div");
  el.className = `bubble ${type}`;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text || sendButton.disabled) return;

  appendBubble(text, "user");
  chatInput.value = "";
  sendButton.disabled = true;

  try {
    const response = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = (await response.json()) as ChatResponse;
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    appendBubble(data.content ?? data.response ?? "No response.", "ai");
  } catch (error) {
    appendBubble(
      `Backend error: ${error instanceof Error ? error.message : String(error)}`,
      "ai"
    );
  } finally {
    sendButton.disabled = false;
    chatInput.focus();
  }
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  void sendMessage();
});

let mx = innerWidth / 2, my = innerHeight / 2;
let cx = 0, cy = 0;

document.addEventListener("mousemove", (e) => {
  mx = e.clientX; my = e.clientY;
});

function blink() {
  sweetyCore.animate(
    [
      { transform: "perspective(420px) scaleY(1)" },
      { transform: "perspective(420px) scaleY(.06)" },
      { transform: "perspective(420px) scaleY(1)" }
    ],
    { duration: 160, easing: "cubic-bezier(.8,0,.2,1)" }
  );
  setTimeout(blink, Math.random() * 4200 + 1800);
}
setTimeout(blink, 2200);

function animate() {
  const r = sweetyButton.getBoundingClientRect();
  const tx = Math.max(-1, Math.min(1, (mx - (r.left + r.width / 2)) / 420));
  const ty = Math.max(-1, Math.min(1, (my - (r.top + r.height / 2)) / 260));
  cx += (tx - cx) * 0.08;
  cy += (ty - cy) * 0.08;

  sweetyCore.style.transform =
    `perspective(420px) rotateY(${cx * 12}deg) rotateX(${-cy * 10}deg)`;
  eyes.forEach((eye) => {
    eye.style.transform = `translate(${cx * 4}px, ${cy * 3}px)`;
  });

  requestAnimationFrame(animate);
}
animate();

void setTransparentWindowBackground();
