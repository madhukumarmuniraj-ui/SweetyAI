"""
SweetyAI Legal Workstation - OCR PDF Docket Parser
Extracts text from scanned/image-based court PDFs using Tesseract and stores case data.
"""

import os
import sys
import sqlite3
import pytesseract
from pdf2image import convert_from_path

DB_NAME = "sweety_cases.db"

def process_court_pdf(pdf_path):
    """Converts PDF pages to images and runs local OCR extraction."""
    if not os.path.exists(pdf_path):
        print(f"[SweetyAI OCR] Error: File '{pdf_path}' not found.")
        return

    print(f"[SweetyAI OCR] Processing document: {pdf_path}...")
    
    # Convert PDF pages to high-res images
    try:
        images = convert_from_path(pdf_path, resolution=300)
    except Exception as e:
        print(f"[SweetyAI OCR] Error converting PDF to images (Is poppler installed?): {e}")
        return

    full_extracted_text = ""
    for i, image in enumerate(images):
        print(f"[SweetyAI OCR] Running OCR on page {i+1}...")
        text = pytesseract.image_to_string(image)
        full_extracted_text += f"\n--- Page {i+1} ---\n" + text

    # Save raw extracted text for review
    txt_output = "extracted_docket.txt"
    with open(txt_output, "w", encoding="utf-8") as f:
        f.write(full_extracted_text)
    
    print(f"[SweetyAI OCR] Extraction complete! Raw text saved to {txt_output}")
    print("\n--- Sample Extracted Text Preview ---")
    print(full_extracted_text[:600] + "...\n-------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 docket_ocr.py <path_to_court_pdf>")
    else:
        process_court_pdf(sys.argv[1])
