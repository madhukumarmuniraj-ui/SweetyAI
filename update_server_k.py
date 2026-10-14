import re

with open("server.py", "r") as f:
    code = f.read()

# Look for retriever setup like similarity_search or as_retriever(search_kwargs={"k": ...})
if "search_kwargs" in code or "k=" in code:
    print("Found retrieval configuration in server.py. Inspecting...")
else:
    print("Searching for vectorstore query calls...")

# Let's print out lines containing similarity_search or retriever calls
for line in code.splitlines():
    if "similarity_search" in line or "as_retriever" in line or "k:" in line or "k=" in line:
        print(line.strip())
