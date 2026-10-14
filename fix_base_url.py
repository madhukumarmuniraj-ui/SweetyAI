with open("sweety.py", "r") as f:
    code = f.read()

# Add BASE_URL if not already present
if "BASE_URL =" not in code:
    code = code.replace("import json", "import json\n\nBASE_URL = \"http://127.0.0.1:8765\"")
    with open("sweety.py", "w") as f:
        f.write(code)
    print("Successfully added BASE_URL to sweety.py!")
else:
    print("BASE_URL is already present.")
