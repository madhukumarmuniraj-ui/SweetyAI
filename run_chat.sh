#!/bin/bash
# Launch the SweetyAI terminal chat companion (local Qwen3-8B, 4-bit on GPU).
cd "$(dirname "$0")"

if [ -x "venv/bin/python" ]; then
  exec venv/bin/python chat.py "$@"
fi

echo "[SweetyAI] venv not found - run: python3 -m venv venv && venv/bin/pip install -r requirements.txt"
exit 1
