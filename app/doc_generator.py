import os
from datetime import datetime

def generate_legal_document(title: str, content: str, doc_type: str = "Legal_Brief") -> str:
    """Generates and saves a formatted legal document to the local workspace directory."""
    output_dir = "./generated_legal_docs"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:30]
    filename = f"{doc_type}_{safe_title}_{timestamp}.md"
    file_path = os.path.join(output_dir, filename)
    
    formatted_content = (
        f"# SWEETY-AI LEGAL INTELLIGENCE REPORT\n"
        f"**Generated For:** Madhukumar Muniraj (KSLU Curriculum)\n"
        f"**Document Type:** {doc_type}\n"
        f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"---\n\n"
        f"## Title: {title}\n\n"
        f"{content}\n\n"
        f"---\n"
        f"*Compiled and audited locally by SweetyAI Core Architecture.*"
    )
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)
        return f"Successfully generated and saved document: {file_path}"
    except Exception as e:
        return f"Failed to generate document: {str(e)}"