"""Single source of truth for where SweetyAI keeps its project/state files.

- Dev (running from the checkout): the project root next to app/.
- Frozen (PyInstaller, getattr(sys, 'frozen')): the backend's working
  directory, which the Electron shell points at the data home (the folder
  containing SweetyAI-Core, knowledge_base_docs, chroma_db, ffmpeg.exe).
- SWEETYAI_HOME overrides everything, for portable installs.
"""

import os
import sys
from pathlib import Path


def project_root() -> Path:
    env_home = os.environ.get("SWEETYAI_HOME")
    if env_home:
        return Path(env_home).resolve()
    if getattr(sys, "frozen", False):
        return Path(os.getcwd()).resolve()
    return Path(__file__).resolve().parents[1]
