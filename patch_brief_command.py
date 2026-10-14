with open("sweety.py", "r") as f:
    code = f.read()

# We need to add the generate_legal_brief function and the parser argument
brief_function = """
def generate_legal_brief(topic):
    try:
        response = requests.post(f"{BASE_URL}/rag-chat", json={"message": topic})
        if response.status_code == 200:
            data = response.json()
            rag_response = data.get('response', '')
            sources = data.get('sources', [])
            
            # Construct Professional IRAC Memo
            memo = f\"\"# LEGAL MEMORANDUM / BRIEF
            
**Topic / Issue:** {topic}
**Date:** 2026-10-14
**Repository:** SweetyAI Legal Database

---

### I. RELEVANT STATUTES & PRECEDENTS (RULE)
{rag_response}

### II. SOURCES CITED
- {', '.join(sources) if sources else 'Local Legal Database'}

### III. LEGAL ANALYSIS & APPLICATION
Based on the retrieved statutory provisions and precedents above, the governing principles apply directly to the legal parameters of the matter. Further factual matching is recommended for comprehensive drafting.

### IV. CONCLUSION
The applicable framework is established by the local legal repository entries cited above.
\"\"\"
            print("\\n" + memo)
            
            # Save to file automatically
            filename = f"legal_brief_{topic.lower().replace(' ', '_')[:30]}.md"
            with open(filename, "w") as bf:
                bf.write(memo)
            print(f"\\n[Success] Legal brief successfully generated and saved to '{filename}'!")
            print("=========================================================\\n")
        else:
            print(f"Error: Server returned status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error to legal server (is server.py running?): {e}")
"""

# Find where to insert the function and parser
target_parser_setup = """    # legal ingest
    i_parser = legal_subparsers.add_parser("ingest", help="Ingest legal document into vector store")
    i_parser.add_argument("--doc-id", required=True, help="Unique document ID")
    i_parser.add_argument("--text", required=True, help="Body text/content")
    i_parser.add_argument("--source", required=True, help="Source citation")"""

new_parser_setup = """    # legal ingest
    i_parser = legal_subparsers.add_parser("ingest", help="Ingest legal document into vector store")
    i_parser.add_argument("--doc-id", required=True, help="Unique document ID")
    i_parser.add_argument("--text", required=True, help="Body text/content")
    i_parser.add_argument("--source", required=True, help="Source citation")

    # legal brief
    b_parser = legal_subparsers.add_parser("brief", help="Generate an automated IRAC legal memorandum")
    b_parser.add_argument("topic", type=str, help="The legal question or research topic")"""

target_dispatch = """        elif args.legal_command == "ingest":
            ingest_doc(args.doc_id, args.text, args.source)
            return"""

new_dispatch = """        elif args.legal_command == "ingest":
            ingest_doc(args.doc_id, args.text, args.source)
            return
        elif args.legal_command == "brief":
            generate_legal_brief(args.topic)
            return"""

if brief_function.strip() not in code:
    # Insert function near top after imports
    code = code.replace("import json", "import json\n" + brief_function)
    code = code.replace(target_parser_setup, new_parser_setup)
    code = code.replace(target_dispatch, new_dispatch)
    with open("sweety.py", "w") as f:
        f.write(code)
    print("Successfully added 'sweety legal brief' command to sweety.py!")
else:
    print("Brief command already present in sweety.py.")
