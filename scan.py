import os

def scan_logs_safely(directory=".", size_threshold_mb=1):
    print(f"=== SAFE LOG FILE AUDIT FOR: {os.path.abspath(directory)} ===\n")
    ignored_dirs = {"node_modules", "venv", ".git", "chroma_db", "models", "build_pyinstaller", "__pycache__"}
    
    found_logs = False
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith(".log"):
                found_logs = True
                filepath = os.path.join(root, file)
                try:
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    print(f"[{'LARGE' if size_mb >= size_threshold_mb else 'NORMAL'}] {filepath} ({size_mb:.2f} MB)")
                except Exception:
                    continue

    if not found_logs:
        print("No log files found.")
    print("\nScan complete.")

if __name__ == "__main__":
    scan_logs_safely()
