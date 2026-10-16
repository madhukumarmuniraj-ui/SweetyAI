import "./styles.css";
import {
  getCurrentWindow,
  LogicalPosition,
  LogicalSize,
} from "@tauri-apps/api/window";

type Role = "user" | "assistant" | "system";

type ChatMessage = {
  id: number;
  role: Role;
  content: string;
};

type ChatResponse = {
  ok: boolean;
  content?: string;
  error?: string;
};

const app = document.querySelector<HTMLDivElement>("#app")!;
const win = getCurrentWindow();

const state = {
  expanded: true,
  busy: false,
  messages: [] as ChatMessage[],
  draft: "",
  nextId: 1,
  backendOnline: true,
};

const BACKEND = "http://127.0.0.1:8765";
const COLLAPSED = { width: 430, height: 70 };
const EXPANDED = { width: 780, height: 650 };

function addMessage(role: Role, content: string) {
  state.messages.push({
    id: state.nextId++,
    role,
    content,
  });
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMessage(message: ChatMessage): string {
  const label =
    message.role === "user"
      ? "You"
      : message.role === "assistant"
        ? "SweetyAI"
        : "System";

  return `
    <article class="message ${message.role}">
      <div class="message-avatar ${message.role}">
        ${message.role === "assistant" ? "✦" : message.role === "user" ? "You" : "!"}
      </div>
      <div class="message-body">
        <div class="message-meta">${label}</div>
        <div class="message-content">${escapeHtml(message.content).replace(/\n/g, "<br>")}</div>
      </div>
    </article>
  `;
}

function render() {
  app.innerHTML = `
    <div class="viewport ${state.expanded ? "is-expanded" : "is-collapsed"}">
      <section class="island" aria-label="SweetyAI">
        <div class="glass-highlight"></div>

        <header class="island-header">
          <button class="identity" id="identityButton" aria-label="Open SweetyAI">
            <span class="sweety-mark" aria-hidden="true">
              <span class="mark-glow"></span>
              <span class="eye eye-left"></span>
              <span class="eye eye-right"></span>
              <span class="mouth"></span>
            </span>
            <span class="identity-copy">
              <strong>SweetyAI</strong>
              <small>${state.busy ? "Thinking" : "Ready to help"}</small>
            </span>
          </button>

          <div class="header-actions">
            <span class="online-pill ${state.backendOnline ? "online" : "offline"}">
              <span class="online-dot"></span>
              ${state.backendOnline ? "Online" : "Offline"}
            </span>
            ${state.expanded ? `
              <button class="round-button" id="clearButton" aria-label="New chat">＋</button>
              <button class="round-button" id="collapseButton" aria-label="Collapse">⌃</button>
            ` : `
              <button class="expand-hint" id="expandButton" aria-label="Expand">⌄</button>
            `}
          </div>
        </header>

        ${state.expanded ? `
          <div class="panel">
            <div class="hero-strip">
              <div class="hero-copy">
                <span class="eyebrow">SWEETYAI</span>
                <h1>What are we building today?</h1>
                <p>Your local AI workspace for chat, files, tools and project work.</p>
              </div>
              <div class="hero-orb" aria-hidden="true">
                <span class="hero-eye left"></span>
                <span class="hero-eye right"></span>
              </div>
            </div>

            <div class="messages" id="messages">
              ${state.messages.length === 0 ? `
                <div class="empty-state">
                  <button class="quick-card" data-prompt="Explain how my SweetyAI tools work.">
                    <span class="quick-icon">⌁</span>
                    <span>
                      <strong>Understand a project</strong>
                      <small>Trace code, tools and execution paths.</small>
                    </span>
                  </button>
                  <button class="quick-card" data-prompt="Create a small test file and verify it.">
                    <span class="quick-icon">＋</span>
                    <span>
                      <strong>Work with files</strong>
                      <small>Create, read and inspect project files.</small>
                    </span>
                  </button>
                  <button class="quick-card" data-prompt="What can you help me with right now?">
                    <span class="quick-icon">✦</span>
                    <span>
                      <strong>Start a conversation</strong>
                      <small>Ask anything and let SweetyAI use its tools.</small>
                    </span>
                  </button>
                </div>
              ` : state.messages.map(renderMessage).join("")}
              ${state.busy ? `
                <article class="message assistant thinking-message">
                  <div class="message-avatar assistant">✦</div>
                  <div class="message-body">
                    <div class="message-meta">SweetyAI</div>
                    <div class="thinking-dots"><span></span><span></span><span></span></div>
                  </div>
                </article>
              ` : ""}
            </div>

            <div class="composer-shell">
              <div class="composer-tools">
                <button class="tool-chip" id="fileChip">＋ File</button>
                <span class="composer-spacer"></span>
                <span class="composer-hint">Enter to send · Shift+Enter for newline</span>
              </div>
              <form class="composer" id="composer">
                <textarea id="input" rows="1" placeholder="Message SweetyAI…" ${state.busy ? "disabled" : ""}>${escapeHtml(state.draft)}</textarea>
                <button class="send-button" type="submit" ${state.busy ? "disabled" : ""} aria-label="Send">
                  <span>↑</span>
                </button>
              </form>
            </div>
          </div>
        ` : `
          <button class="collapsed-lower" id="collapsedPrompt">
            <span class="collapsed-prompt-dot"></span>
            <span>${state.messages.length ? "Continue your conversation" : "Ask SweetyAI anything"}</span>
            <span class="collapsed-arrow">↗</span>
          </button>
        `}
      </section>
    </div>
  `;

  wireEvents();

  if (state.expanded) {
    const messages = document.querySelector<HTMLDivElement>("#messages");
    if (messages) messages.scrollTop = messages.scrollHeight;

    const input = document.querySelector<HTMLTextAreaElement>("#input");
    if (input) {
      autoResize(input);
      if (state.busy) {
        input.blur();
      }
    }
  }
}

function wireEvents() {
  document.querySelector("#identityButton")?.addEventListener("click", () => {
    if (state.expanded) return;
    expand();
  });

  document.querySelector("#expandButton")?.addEventListener("click", expand);
  document.querySelector("#collapsedPrompt")?.addEventListener("click", expand);
  document.querySelector("#collapseButton")?.addEventListener("click", collapse);

  document.querySelector("#clearButton")?.addEventListener("click", () => {
    state.messages = [];
    state.draft = "";
    render();
    setTimeout(() => document.querySelector<HTMLTextAreaElement>("#input")?.focus(), 40);
  });

  document.querySelectorAll<HTMLButtonElement>(".quick-card").forEach((button) => {
    button.addEventListener("click", () => {
      const prompt = button.dataset.prompt || "";
      state.draft = prompt;
      render();
      const input = document.querySelector<HTMLTextAreaElement>("#input");
      input?.focus();
      input?.setSelectionRange(prompt.length, prompt.length);
    });
  });

  document.querySelector("#fileChip")?.addEventListener("click", () => {
    addMessage("system", "File drop is ready for the next integration pass. Your existing Python backend remains unchanged.");
    render();
  });

  const composer = document.querySelector<HTMLFormElement>("#composer");
  composer?.addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendMessage();
  });

  const input = document.querySelector<HTMLTextAreaElement>("#input");
  input?.addEventListener("input", () => {
    state.draft = input.value;
    autoResize(input);
  });

  input?.addEventListener("keydown", async (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      await sendMessage();
    }
  });
}

function autoResize(input: HTMLTextAreaElement) {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 150)}px`;
}

async function sendMessage() {
  const content = state.draft.trim();
  if (!content || state.busy) return;

  addMessage("user", content);
  state.draft = "";
  state.busy = true;
  state.backendOnline = true;
  render();

  try {
    const response = await fetch(`${BACKEND}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: content }),
    });

    const data = (await response.json()) as ChatResponse;

    if (!response.ok || !data.ok) {
      throw new Error(data.error || `Backend returned ${response.status}`);
    }

    addMessage("assistant", data.content || "");
  } catch (error) {
    state.backendOnline = false;
    addMessage(
      "system",
      `SweetyAI backend unavailable: ${error instanceof Error ? error.message : String(error)}`,
    );
  } finally {
    state.busy = false;
    render();
  }
}

async function expand() {
  state.expanded = true;
  render();
  setTimeout(() => document.querySelector<HTMLTextAreaElement>("#input")?.focus(), 100);
}

async function collapse() {
  state.expanded = false;
  render();
}

function startup() {
  state.expanded = true;
  render();
  setTimeout(() => document.querySelector<HTMLTextAreaElement>("#input")?.focus(), 250);
}

startup();
