with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

# Clean any accidental non-breaking spaces
code = code.replace("\u00a0", " ")

early_intercept = """import sys
if len(sys.argv) > 1 and sys.argv[1] == "export":
    from document_exporter import export_document
    if len(sys.argv) > 2:
        export_document(sys.argv[2])
    else:
        print("Usage: python3 sweety.py export <file.md>")
    sys.exit(0)
"""

if 'sys.argv[1] == "export"' not in code or "sys.exit(0)" not in code:
    code = early_intercept + "\n" + code

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[Success] Export interceptor placed at top of sweety.py (bypasses torch load)!")
