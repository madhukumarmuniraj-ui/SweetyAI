import os
os.environ["HF_HUB_OFFLINE"] = "1"  # strictly local: use the SweetyAI-Core checkpoint

import re
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from app.memory import add_message, get_recent_history
from app.tools import AVAILABLE_TOOLS

# Local SweetyAI Core checkpoint (Qwen3-8B, run 4-bit on the GPU)
MODEL_PATH = "./SweetyAI-Core"

print("Loading SweetyAI Core tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)

print("Configuring 4-bit quantization...")
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

print("Loading Qwen 8B in 4-bit (local SweetyAI-Core checkpoint)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=quant_config,
    device_map={"": 0},
    local_files_only=True,
)

print("\n==================================================")
print("   SweetyAI Terminal Companion (Professional)")
print("==================================================")
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
print("VRAM allocated:",
      round(torch.cuda.memory_allocated(0) / 1024**3, 2),
      "GB")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Save user message to SQLite persistent memory
    add_message("user", user_input)

    # Dynamic Local Tool Interceptors (Explicit triggers only)
    user_lower = user_input.strip().lower()
    tool_output = None

    if user_lower in ["/time", "what time is it", "current time", "date today"]:
        try:
            tool_output = AVAILABLE_TOOLS["get_current_time"]()
        except Exception as e:
            tool_output = f"Tool error: {e}"
            
    elif user_lower in ["/folder", "open workspace"]:
        try:
            tool_output = AVAILABLE_TOOLS["open_workspace_folder"]()
        except Exception as e:
            tool_output = f"Tool error: {e}"
            
    elif user_lower in ["/files", "list documents"]:
        try:
            tool_output = AVAILABLE_TOOLS["list_knowledge_documents"]()
        except Exception as e:
            tool_output = f"Tool error: {e}"
            
    elif user_lower.startswith("/calc ") or user_lower.startswith("calc "):
        expr = user_lower.replace("/calc", "").replace("calc", "").strip()
        try:
            tool_output = AVAILABLE_TOOLS["calculator"](expr)
        except Exception as e:
            tool_output = f"Tool error: {e}"

    # Fetch recent chat context from SQLite
    chat_history = get_recent_history(limit=4)

    # Strict System Prompt: Binds SweetyAI to direct, professional, concise answers
    system_prompt = (
        "You are SweetyAI, a precise, professional local desktop intelligence "
        "compiled exclusively for Madhukumar Muniraj. "
        "Rules: Provide direct, concise, and professional responses. "
        "Never generate internal monologues, thinking blocks, meta-commentary, or playful joking."
    )

    system_parts = [system_prompt]
    if chat_history:
        system_parts.append(f"[Recent Conversation History]:\n{chat_history}")

    if tool_output is not None:
        system_parts.append(f"[Local Tool Execution Result]:\n{tool_output}")

    messages = [
        {"role": "system", "content": "\n\n".join(system_parts)},
        {"role": "user", "content": user_input},
    ]
    try:
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
    except TypeError:
        prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(
        [prompt_text],
        return_tensors="pt"
    ).to("cuda")

    print("\nSweetyAI is thinking...\n")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,         # Keep responses short and focused
            do_sample=True,
            temperature=0.2,           # Low temperature for strict adherence
            top_p=0.85,
            repetition_penalty=1.2,    # Heavy penalty against looping
        )

    response = outputs[0][inputs.input_ids.shape[1]:]
    raw_answer = tokenizer.decode(response, skip_special_tokens=True).strip()

    # Aggressive cleaning of any stray thinking tags or bracketed thoughts
    clean_answer = re.sub(r'<think>[\s\S]*?</think>', '', raw_answer)
    clean_answer = re.sub(r'\[.*?Thought.*?\]:[\s\S]*?(?=\[Answer\]|AI:|$)', '', clean_answer, flags=re.IGNORECASE)
    clean_answer = clean_answer.replace("[Answer]:", "").replace("Final Answer:", "").strip()

    print("AI:", clean_answer)
    print()

    # Save assistant response to SQLite persistent memory
    add_message("assistant", clean_answer)