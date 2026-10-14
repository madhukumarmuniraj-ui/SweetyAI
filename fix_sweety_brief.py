with open("sweety.py", "r") as f:
    lines = f.readlines()

# Let's clean up any broken brief function or add it properly
# First, let's remove any old broken brief function lines if present
cleaned_lines = []
skip = False
for line in lines:
    if "def generate_legal_brief" in line:
        skip = True
    if skip:
        if "if args.command == " in line or "def " in line and "generate_legal_brief" not in line:
            skip = False
    if not skip:
        cleaned_lines.append(line)

with open("sweety.py", "w") as f:
    f.writelines(cleaned_lines)

print("Cleaned sweety.py successfully.")
