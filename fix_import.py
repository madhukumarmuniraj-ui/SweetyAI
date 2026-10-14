with open("sweety_cua.py", "r") as f:
    content = f.read()

if "import os" not in content:
    content = "import os\nimport subprocess\nimport time\nimport urllib.parse\nfrom PIL import Image\n" + content

with open("sweety_cua.py", "w") as f:
    f.write(content)

print("[Success] Imports added!")
