import pytest
import os
import tempfile
from rag import recursive_chunk_text, ingest_document, search_knowledge_base

def test_recursive_chunk_text():
    sample_text = "SweetyAI is an intelligent desktop assistant. " * 50
    chunks = recursive_chunk_text(sample_text, chunk_size=300, chunk_overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) > 0

def test_ingest_and_search_document():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Article 21 guarantees protection of life and personal liberty in Indian constitutional law.")
        temp_file = f.name

    try:
        success = ingest_document(temp_file)
        assert success is True

        results = search_knowledge_base("Article 21 personal liberty", n_results=1)
        assert "Article 21" in results or len(results) > 0
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
