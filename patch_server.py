with open("server.py", "r") as f:
    code = f.read()

# Replace n_results=2 with n_results=4 for deeper multi-chunk retrieval
old_query = """        results = collection.query(
            query_texts=[data.message],
            n_results=2
        )"""

new_query = """        results = collection.query(
            query_texts=[data.message],
            n_results=4
        )"""

if old_query in code:
    code = code.replace(old_query, new_query)
    with open("server.py", "w") as f:
        f.write(code)
    print("Successfully updated server.py to retrieve 4 chunks!")
else:
    print("Could not find exact block, checking alternative patterns...")
