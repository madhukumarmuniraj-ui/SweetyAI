document.addEventListener("DOMContentLoaded", () => {
  const textInput = document.getElementById("textInput");
  const floatingContainer = document.getElementById("floatingContainer");
  const micBtn = document.getElementById("micBtn");
  const sendBtn = document.getElementById("sendBtn");
  const agentLogo = document.getElementById("agentLogo");
  const contextualMenu = document.getElementById("contextualMenu");

  // Handle typing: Text floats upward / updates preview container
  textInput.addEventListener("input", (e) => {
const { ipcMain } = require('electron');
ipcMain.handle('ai-chat-message', async (event, message) => {
    // Call your local model backend or API here
    return `Echo from Sweety AI backend: ${message}`;
});    
const val = e.target.value.trim();
    if (val.length > 0) {
      floatingContainer.textContent = val;
      floatingContainer.classList.add("active");
    } else {
      floatingContainer.classList.remove("active");
    }
  });

  // Left-Click on agent logo: Opens Chat view
  if (agentLogo) {
    agentLogo.addEventListener("click", (e) => {
      e.preventDefault();
      console.log("Chat view opened via Left-Click.");
      // Add custom chat-opening logic here
    });

    // Right-Click on agent logo & composer icons: Opens Contextual Menu
    agentLogo.addEventListener("contextmenu", handleContextMenu);
  }

  // Right-Click on composer icons (Mic & Send) for Contextual Menu
  [micBtn, sendBtn].forEach((btn) => {
    if (btn) {
      btn.addEventListener("contextmenu", handleContextMenu);
    }
  });

  function handleContextMenu(e) {
    e.preventDefault();
    const rect = e.currentTarget.getBoundingClientRect();
    
    // Position menu near the click target
    contextualMenu.style.left = `${rect.left}px`;
    contextualMenu.style.top = `${rect.top - 110}px`;
    contextualMenu.classList.toggle("visible");
  }

  // Close contextual menu on external clicks
  document.addEventListener("click", (e) => {
    if (!contextualMenu.contains(e.target)) {
      contextualMenu.classList.remove("visible");
    }
  });

  // Action handlers for buttons
  micBtn.addEventListener("click", () => {
    console.log("Microphone clicked for voice input.");
  });

  sendBtn.addEventListener("click", () => {
    if (textInput.value.trim() !== "") {
      console.log("Sending message:", textInput.value);
      textInput.value = "";
      floatingContainer.classList.remove("active");
    }
  });
});