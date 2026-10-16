import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import torch

import transformers.modeling_utils
# Disable aggressive Windows CUDA warmup that causes phantom OOM
transformers.modeling_utils.caching_allocator_warmup = lambda *args, **kwargs: None


from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from app.agent.agent import Agent

# Force offline mode so everything stays strictly local to your machine
os.environ["HF_HUB_OFFLINE"] = "1"

MODEL_PATH = "./SweetyAI-Core"


def load_model():
    print("Loading SweetyAI tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )

    print("Loading SweetyAI Engine in 4-bit...")

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        quantization_config=quant_config,
        device_map={"": 0},
        local_files_only=True,
    )

    # Overwrite in-memory model identity to SweetyAI
    model.config._name_or_path = "SweetyAI-Core"

    return tokenizer, model


def main():
    tokenizer, model = load_model()

    agent = Agent(
        model=model,
        tokenizer=tokenizer,
    )

    print()
    print("==============================")
    print("        SWEETY AI")
    print("==============================")
    print("GPU:", torch.cuda.get_device_name(0))
    print("Type 'exit' to quit.")
    print()

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        print("\nSweety is thinking...\n")

        answer = agent.chat(user_input)

        print("SweetyAI:", answer)
        print()


if __name__ == "__main__":
    main()