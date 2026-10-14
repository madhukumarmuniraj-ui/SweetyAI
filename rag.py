import os
import time
import chromadb

# Initialize persistent ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="sweety_knowledge_base")

def recursive_chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[str]:
    """Splits text into overlapping chunks with clean paragraph and sentence boundaries."""
    if not text or not text.strip():
        return []

    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(text_to_split: str, seps: list[str]) -> list[str]:
        if not seps or len(text_to_split) <= chunk_size:
            return [text_to_split] if text_to_split.strip() else []

        sep = seps[0]
        splits = text_to_split.split(sep)
        chunks = []
        current_chunk = ""

        for part in splits:
            candidate = current_chunk + (sep if current_chunk else "") + part
            if len(candidate) <= chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(part) > chunk_size:
                    sub_chunks = _split(part, seps[1:])
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part

        if current_chunk and current_chunk.strip():
            chunks.append(current_chunk)

        # Apply overlap
        if chunk_overlap > 0 and len(chunks) > 1:
            overlapped = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    prev_tail = chunks[i-1][-chunk_overlap:]
                    overlapped.append(prev_tail + " " + chunk)
                else:
                    overlapped.append(chunk)
            return overlapped
        return chunks

    return _split(text, separators)

def search_knowledge_base(query: str, n_results: int = 2) -> str:
    """
    Searches the ChromaDB collection for text relevant to the user's query.
    """
    if not query or not query.strip():
        return ""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        documents = results.get("documents", [[]])[0]
        if documents:
            return "\n---\n".join(documents)
        return ""
    except Exception as e:
        print(f"[RAG Search Error]: {e}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """Extracts text content from various supported document formats."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages)
        except Exception:
            pass

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def ingest_document(file_path: str) -> bool:
    """
    Reads a document, chunks it with overlap, and adds it to the ChromaDB vector database.
    """
    try:
        if not os.path.exists(file_path):
            print(f"[RAG Ingest Error] File not found: {file_path}")
            return False

        text = extract_text_from_file(file_path)
        if not text.strip():
            print(f"[RAG Ingest Warning] File has no extractable text: {file_path}")
            return False

        chunks = recursive_chunk_text(text, chunk_size=800, chunk_overlap=150)
        if not chunks:
            chunks = [text[:800]]

        filename = os.path.basename(file_path)
        timestamp = int(time.time())
        ids = [f"{filename}_chunk_{i}_{timestamp}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i, "total_chunks": len(chunks)} for i in range(len(chunks))]

        collection.upsert(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"[RAG Success] Successfully ingested {len(chunks)} chunks from {filename}")
        return True

    except Exception as e:
        print(f"[RAG Ingestion Error]: {e}")
        return False
