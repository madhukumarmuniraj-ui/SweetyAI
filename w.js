document.addEventListener("DOMContentLoaded", () => {
  const logoWrapper = document.getElementById("coucou-logo-wrapper");
  const chatbox = document.getElementById("sweety-chatbox");
  const closeChat = document.getElementById("close-chat");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const thinkingDots = document.getElementById("thinking-dots");

  // Toggle Chatbox on Logo Click
  if (logoWrapper && chatbox) {
    logoWrapper.addEventListener("click", () => {
      chatbox.classList.toggle("hidden");
    });
  }

  // Close Chat button
  if (closeChat && chatbox) {
    closeChat.addEventListener("click", () => {
      chatbox.classList.add("hidden");
    });
  }

  // Send button handler & simulated thinking state
  if (sendBtn && chatInput) {
    sendBtn.addEventListener("click", () => {
      const message = chatInput.value.trim();
      if (message !== "") {
        console.log("Sending message:", message);
        
        // Show thinking dots inside the companion circle
        if (thinkingDots) thinkingDots.classList.remove("hidden");

        // Simulate backend response after 2 seconds
        setTimeout(() => {
          if (thinkingDots) thinkingDots.classList.add("hidden");
          addChatMessage("SweetyAI", `Received: ${message}`);
        }, 2000);

        chatInput.value = "";
      }
    });

    // Allow Enter key to send
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        sendBtn.click();
      }
    });
  }

  // Sub-options handlers (Attach, Camera, Menu, History)
  const attachBtn = document.getElementById("action-attach");
  const cameraBtn = document.getElementById("action-camera");
  const menuBtn = document.getElementById("action-menu");
  const historyBtn = document.getElementById("action-history");

  if (attachBtn) attachBtn.addEventListener("click", () => console.log("Attach clicked"));
  if (cameraBtn) cameraBtn.addEventListener("click", () => console.log("Camera clicked"));
  if (menuBtn) menuBtn.addEventListener("click", () => console.log("Menu clicked"));
  if (historyBtn) historyBtn.addEventListener("click", () => console.log("History clicked"));

  function addChatMessage(sender, text) {
    const chatMessages = document.getElementById("chat-messages");
    if (chatMessages) {
      const bubble = document.createElement("div");
      bubble.className = "p-2 bg-white/10 rounded-xl text-xs text-white flex flex-col gap-1";
      bubble.innerHTML = `<span class="font-semibold text-amber-400">${sender}</span><span>${text}</span>`;
      chatMessages.appendChild(bubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }
});