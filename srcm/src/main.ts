// Replace triggerStartupGreeting with this user-triggered or click-unlocked version
let hasGreeted = false;

async function triggerStartupGreeting(): Promise<void> {
  if (hasGreeted) return;
  hasGreeted = true;
  
  const welcomeText = "Hello Madhukumar. SweetyAI is online and listening. What legal research or tasks shall we tackle today?";
  appendMessage(welcomeText, "msg-ai");
  await speakText(welcomeText);
}

// Trigger the greeting the moment you click anywhere or open the chat for the first time
document.addEventListener("click", () => {
  void triggerStartupGreeting();
}, { once: true });