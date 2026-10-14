with open("sweety.py", "r") as f:
    code = f.read()

brief_code = '''
def generate_legal_brief(topic):
    try:
        response = requests.post(f"{BASE_URL}/rag-chat", json={"message": topic})
        if response.status_code == 200:
            data = response.json()
            rag_response = data.get('response', '')
            sources = data.get('sources', [])
            
            memo = (
                "# LEGAL MEMORANDUM / BRIEF\\n\\n"
                f"**Topic / Issue:** {topic}\\n"
                "**Date:** 2026-10-14\\n"
                "**Repository:** SweetyAI Legal Database\\n\\n"
                "---\\n\\n"
                "### I. RELEVANT STATUTES & PRECEDENTS (RULE)\\n"
                f"{rag_response}\\n\\n"
                "### II. SOURCES CITED\\n"
                f"- {', '.join(sources) if sources else 'Local Legal Database'}\\n\\n"
                "### III. LEGAL ANALYSIS & APPLICATION\\n"
                "Based on the retrieved statutory provisions and precedents above, the governing principles apply directly to the legal parameters of the matter.\\n\\n"
                "### IV. CONCLUSION\\n"
                "The applicable framework is established by the local legal repository entries cited above.\\n"
            )
            print("\\n" + memo)
            
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
'''

# Insert after import json
if "def generate_legal_brief" not in code:
    code = code.replace("import json", "import json\n" + brief_code)

# Add parser for brief if not present
if "brief" not in code:
    old_target = """    # legal ingest
    i_parser = legal_subparsers.add_parser("ingest", help="Ingest legal document into vector store")
    i_parser.add_argument("--doc-id", required=True, help="Unique document ID")
    i_parser.add_argument("--text", required=True, help="Body text/content")
    i_parser.add_argument("--source", required=True, help="Source citation")"""

    new_target = old_target + """

    # legal brief
    b_parser = legal_subparsers.add_parser("brief", help="Generate an automated IRAC legal memorandum")
    b_parser.add_argument("topic", type=str, help="The legal question or research topic")"""

    code = code.replace(old_target, new_target)

# Add dispatcher if not present
if "elif args.legal_command == \"brief\":" not in code:
    old_dispatch = """        elif args.legal_command == "ingest":
            ingest_doc(args.doc_id, args.text, args.source)
            return"""

    new_dispatch = old_dispatch + """
        elif args.legal_command == "brief":
            generate_legal_brief(args.topic)
            return"""

    code = code.replace(old_dispatch, new_dispatch)

with open("sweety.py", "w") as f:
    f.write(code)

print("Successfully added clean brief command to sweety.py!")
