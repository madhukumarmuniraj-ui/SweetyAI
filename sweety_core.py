#!/home/madhukumarm/SweetyAI/venv/bin/python3
import os
import sys
import re
import json
import sqlite3
import subprocess
from datetime import datetime

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

BASE_DIR = "/home/madhukumarm/SweetyAI"
os.chdir(BASE_DIR)

for vdir in ["venv", ".venv"]:
    lib_dir = os.path.join(BASE_DIR, vdir, "lib")
    if os.path.exists(lib_dir):
        for py_ver in os.listdir(lib_dir):
            sp = os.path.join(lib_dir, py_ver, "site-packages")
            if os.path.exists(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


class DualModelRouter:
    """Smart router that routes light work to the small model and heavy/legal work to the large model."""

    _small_engine = None
    _large_engine = None
    _loaded = {}  # model_path -> loaded runtime (Llama instance or (tokenizer, model))

    @classmethod
    def discover_and_load_models(cls):
        if cls._small_engine is not None or cls._large_engine is not None:
            return

        ggufs = []
        hf_folders = []

        for mdir in ["models", "SweetyAI-Core", "checkpoints", "cache_small"]:
            pdir = os.path.join(BASE_DIR, mdir)
            if os.path.exists(pdir):
                for root, dirs, files in os.walk(pdir):
                    for f in files:
                        if f.endswith(".gguf"):
                            ggufs.append(os.path.join(root, f))
                    if "config.json" in files and any(x.endswith((".safetensors", ".bin")) for x in files):
                        hf_folders.append(root)

        # Light route prefers a GGUF (CPU friendly); the deep legal route prefers
        # the full HuggingFace checkpoint (SweetyAI-Core, runs 4-bit on GPU).
        if ggufs and hf_folders:
            cls._small_engine = ggufs[0]
            cls._large_engine = hf_folders[0]
        elif ggufs:
            cls._small_engine = ggufs[0]
            cls._large_engine = ggufs[-1]
        elif hf_folders:
            cls._small_engine = hf_folders[0]
            cls._large_engine = hf_folders[0]

    @classmethod
    def _run_on_model(cls, target_model: str, model_type: str, prompt: str, context: str) -> str:
        # Execute GGUF via llama_cpp
        if target_model.endswith(".gguf"):
            full_prompt = (
                f"Context:\n{context[:4000]}\n\nUser: {prompt}\nSweety:"
                if context else f"User: {prompt}\nSweety:"
            )
            try:
                llm = cls._loaded.get(target_model)
                if llm is None:
                    from llama_cpp import Llama
                    n_ctx = 1024 if model_type == "small" else 2048
                    n_threads = 2 if model_type == "small" else 4
                    llm = Llama(model_path=target_model, n_ctx=n_ctx, n_threads=n_threads, n_gpu_layers=0, verbose=False)
                    cls._loaded[target_model] = llm
                max_t = 128 if model_type == "small" else 300
                out = llm(full_prompt, max_tokens=max_t, stop=["User:", "\nUser:"])
                if "choices" in out and out["choices"]:
                    return out["choices"][0]["text"].strip()
            except Exception:
                pass
            return ""

        # Execute HuggingFace Transformers
        if os.path.isdir(target_model):
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForCausalLM

                runtime = cls._loaded.get(target_model)
                if runtime is None:
                    tokenizer = AutoTokenizer.from_pretrained(target_model, local_files_only=True)
                    load_kwargs = dict(local_files_only=True, low_cpu_mem_usage=True)
                    try:
                        from transformers import BitsAndBytesConfig
                        if torch.cuda.is_available():
                            # 4-bit on GPU: the 8B core fits in ~6 GB VRAM
                            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                                load_in_4bit=True,
                                bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.bfloat16,
                                bnb_4bit_use_double_quant=True,
                            )
                            load_kwargs["device_map"] = {"": 0}
                        else:
                            # No GPU: 4-bit keeps the memory footprint viable on CPU
                            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
                    except Exception:
                        pass
                    model = AutoModelForCausalLM.from_pretrained(target_model, **load_kwargs)
                    model.eval()
                    runtime = (tokenizer, model)
                    cls._loaded[target_model] = runtime

                tokenizer, model = runtime
                device = getattr(model, "device", torch.device("cpu"))

                # Build the input with the model's chat template (clean turn boundaries)
                system = (
                    "You are Sweety, an offline Indian legal AI workstation assistant. "
                    + ("Provide deep, precise legal analysis." if model_type == "large" else "Be concise and direct.")
                )
                user = f"Context:\n{context[:4000]}\n\nUser: {prompt}" if context else prompt
                messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
                try:
                    text = tokenizer.apply_chat_template(
                        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
                    )
                except TypeError:
                    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                except Exception:
                    text = f"User: {prompt}\nSweety:"

                inputs = tokenizer(text, return_tensors="pt").to(device)
                with torch.no_grad():
                    max_new = 200 if model_type == "small" else 500
                    output_ids = model.generate(
                        **inputs, max_new_tokens=max_new, do_sample=True, temperature=0.6,
                        pad_token_id=tokenizer.eos_token_id
                    )
                gen = tokenizer.decode(output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
                if gen:
                    return gen
            except Exception:
                pass
            return ""

        return ""

    @classmethod
    def run_inference(cls, prompt: str, model_type: str = "small", context: str = "") -> str:
        cls.discover_and_load_models()
        target_model = cls._large_engine if model_type == "large" else cls._small_engine

        if not target_model:
            return f"SweetyAI Core executed via {model_type.upper()} Model route for: '{prompt}'."

        answer = cls._run_on_model(target_model, model_type, prompt, context)

        # Fallback: if the preferred engine is unavailable (e.g. llama_cpp is not
        # installed for the GGUF route), answer via the other engine instead.
        if not answer:
            other = cls._small_engine if model_type == "large" else cls._large_engine
            if other and other != target_model:
                other_type = "large" if other == cls._large_engine else "small"
                answer = cls._run_on_model(other, other_type, prompt, context)

        return answer


class SweetyBrain:
    @staticmethod
    def classify_workload(query: str) -> str:
        """Determines if the prompt is light work or heavy/legal work."""
        q_low = query.lower()
        heavy_keywords = [
            "pdf", "read", "ingest", "draft", "petition", "bail", "138", "writ",
            "suit", "appeal", "complaint", "contract", "review", "court fee",
            "valuation", "audit", "quash", "arbitration", "ibc", "code", "debug"
        ]
        if any(k in q_low for k in heavy_keywords) or len(query.split()) > 15:
            return "large"
        return "small"

    @classmethod
    def respond(cls, user_input: str) -> str:
        u = user_input.strip()
        workload_type = cls.classify_workload(u)
        
        print(f"[*] Sweety Dual-Model Router: Routing '{u[:30]}...' to [{workload_type.upper()} model]...")

        # Run the appropriate model
        answer = DualModelRouter.run_inference(u, model_type=workload_type)
        if answer:
            return answer

        # Fallback response if model weights are not loaded
        return f"SweetyAI Core executed via {workload_type.upper()} Model route for: '{u}'."


def generate_response(prompt: str) -> str:
    return SweetyBrain.respond(prompt)
