# legal_tool.py
import json
import os

def search_legal_database(query: str) -> str:
    """
    Searches local legal statutes, case laws, and KSLU curriculum notes 
    for precise legal rules, articles, and administrative provisions.
    """
    print(f"[Legal Tool] Searching legal database for: {query}")
    
    # Path to your local legal notes or JSON/TXT file database
    db_path = "legal_database.json"
    if not os.path.exists(db_path):
        # Fallback default sample provisions if database file doesn't exist yet
        sample_legal_data = {
            "administrative law": "Administrative law governs the activities of administrative agencies of government, including rule making, adjudication, and the enforcement of laws.",
            "competition law": "Competition law promotes or seeks to maintain market competition by regulating anti-competitive conduct by companies.",
            "contract": "A contract is a voluntary, legally binding agreement between two or more competent parties."
        }
        with open(db_path, "w") as f:
            json.dump(sample_legal_data, f, indent=2)

    with open(db_path, "r") as f:
        data = json.load(f)

    query_lower = query.lower()
    results = []
    for key, val in data.items():
        if key in query_lower or query_lower in key:
            results.append(f"[{key.upper()}]: {val}")

    if not results:
        return f"No direct statutory match found for '{query}'. Proceeding with standard RAG vector memory search."
    
    return "\n".join(results)