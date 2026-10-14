with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Inject the pysqlite3 workaround at the very top of server.py
patch = """import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
"""

if "pysqlite3" not in code:
    code = patch + code
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SQLite patch applied to server.py!")
else:
    print("SQLite patch already present.")
