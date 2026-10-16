"""SweetyAI primary launcher entry point.

Delegates to the enterprise legal workstation CLI (`sweety.py`), which hosts
the unified fast-path router for all 108+ legal modules.

Usage:
    python3 main.py                 # prints the workstation usage banner
    python3 main.py legal bail ...  # routes straight to a legal module
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SWEETY_CLI = os.path.join(ROOT, "sweety.py")


def build_command(argv=None):
    """Build the (interpreter, sweety.py, *args) command line to execute."""
    args = list(sys.argv[1:] if argv is None else argv)
    return [sys.executable, SWEETY_CLI] + args


def main(argv=None):
    cmd = build_command(argv)
    if len(cmd) > 2:
        print(f"[SweetyAI] Launching: {' '.join(cmd[2:])}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
