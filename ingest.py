import os
from rag import add_document_to_db

def ingest_folder(folder_path="./docs"):
    """Reads all text files from a folder and adds them to ChromaDB."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created '{folder_path}' folder. Drop your text/legal notes there!")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            path = os.path.join(folder_path, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                add_document_to_db(doc_id=filename, text=content, metadata={"source": filename})

if __name__ == "__main__":
    ingest_folder()