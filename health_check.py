import os

print("=== SWEETYAI WORKSPACE HEALTH AUDIT ===")
print(f"Working Directory: {os.getcwd()}")

core_files = ["app/agent/agent.py", "app/agent/tools.py", "app/tools/master_registry.py", "server.py"]
print("\n[Core Components Check]")
for f in core_files:
    exists = os.path.exists(f)
    status = "[OK]" if exists else "[MISSING]"
    print(f" - {f}: {status}")

db_folders = ["chroma_db", "sweety_vectordb", "sweetyai_legal_db"]
print("\n[Vector & Database Storage Check]")
for db in db_folders:
    if os.path.exists(db):
        try:
            total_size = sum(os.path.getsize(os.path.join(root, file)) for root, dirs, files in os.walk(db) for file in files) / (1024 * 1024)
            print(f" - {db}/ ({total_size:.2f} MB)")
        except Exception:
            print(f" - {db}/ (Size calculation error)")
    else:
        print(f" - {db}/: [Not Initialized]")

print("\nHealth check complete!")
