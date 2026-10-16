"""
SweetyAI Legal Workstation - Local Precedent RAG Engine
Performs lightning-fast semantic search over local legal briefs and judgments.
"""

import os
import sys
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Use a lightweight, high-performance local embedding model
MODEL_NAME = "all-MiniLM-L6-v2"
PRECEDENTS_DIR = "precedents"
INDEX_FILE = "precedents.index"
DOCS_FILE = "precedents_docs.txt"

def load_model():
    print(f"[SweetyAI RAG] Loading local embedding model ({MODEL_NAME})...")
    return SentenceTransformer(MODEL_NAME)

def build_index():
    """Scans the precedents/ directory, embeds documents, and builds a FAISS index."""
    if not os.path.exists(PRECEDENTS_DIR):
        os.makedirs(PRECEDENTS_DIR)
        print(f"[SweetyAI RAG] Created '{PRECEDENTS_DIR}/' folder. Place your legal text briefs/judgments there!")
        return

    files = [f for f in os.listdir(PRECEDENTS_DIR) if f.endswith(('.txt', '.md'))]
    if not files:
        print(f"[SweetyAI RAG] No text documents found in '{PRECEDENTS_DIR}/'. Add some briefs to index!")
        return

    documents = []
    for file in files:
        path = os.path.join(PRECEDENTS_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # Split into chunks or keep full file
            documents.append(f"[{file}]\n" + content)

    print(f"[SweetyAI RAG] Embedding {len(documents)} legal documents...")
    model = load_model()
    embeddings = model.encode(documents, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and docs
    faiss.write_index(index, INDEX_FILE)
    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        f.write("\n---DOC_SPLIT---\n".join(documents))

    print(f"[SweetyAI RAG] Successfully indexed {len(documents)} documents into '{INDEX_FILE}'!")

def search_precedents(query_text):
    """Searches the local vector index for precedents matching the query."""
    if not os.path.exists(INDEX_FILE) or not os.path.exists(DOCS_FILE):
        print("[SweetyAI RAG] No index found. Run with 'build' first.")
        return

    model = load_model()
    index = faiss.read_index(INDEX_FILE)

    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        documents = f.read().split("\n---DOC_SPLIT---\n")

    print(f"[SweetyAI RAG] Searching for: '{query_text}'...")
    query_vector = model.encode([query_text]).astype('float32')
    
    # Retrieve top 3 matches
    k = min(3, len(documents))
    distances, indices = index.search(query_vector, k)

    print("\n================ TOP LEGAL PRECEDENTS FOUND ================")
    for i, idx in enumerate(indices[0]):
        if idx < len(documents):
            print(f"\nResult {i+1} (Distance Score: {distances[0][i]:.4f}):")
            print(documents[idx][:800] + "...\n" + "-"*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 legal_rag.py build          (Indexes files in precedents/)")
        print("  python3 legal_rag.py 'your query'   (Searches indexed precedents)")
    elif sys.argv[1] == "build":
        build_index()
    else:
        search_precedents(" ".join(sys.argv[1:]))
