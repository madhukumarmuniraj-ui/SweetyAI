@echo off
REM Builds the standalone Python backend (SweetyServer) with PyInstaller.
REM Output: backend_dist\SweetyServer\SweetyServer.exe — run it from a folder
REM that contains SweetyAI-Core + chroma_db + knowledge_base_docs (e.g. C:\SweetyAI).
python -m PyInstaller --noconfirm --onedir --name SweetyServer ^
  --distpath backend_dist --workpath build_pyinstaller ^
  --hidden-import gguf --hidden-import faster_whisper ^
  --collect-submodules chromadb ^
  --collect-all imageio_ffmpeg ^
  --copy-metadata gguf --copy-metadata tokenizers --copy-metadata safetensors ^
  --copy-metadata huggingface-hub --copy-metadata tqdm --copy-metadata regex ^
  --copy-metadata filelock ^
  --add-data "app/legal/legal_playbook.json;app/legal" ^
  --add-data "app/data/semantic_graph.json;app/data" ^
  server.py
