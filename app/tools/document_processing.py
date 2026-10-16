"""
SweetyAI Document Processing Tools
Handles DOCX, Excel, PowerPoint, PDF, and OCR operations
"""

import os
import sys
from typing import Dict, List, Optional, Any
import tempfile

# Document processing libraries
try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("[Document Tools] python-docx not available")

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    import pandas as pd
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("[Document Tools] openpyxl/pandas not available")

try:
    from pptx import Presentation
    from pptx.util import Inches as PptxInches, Pt as PptxPt
    PPT_AVAILABLE = True
except ImportError:
    PPT_AVAILABLE = False
    print("[Document Tools] python-pptx not available")

try:
    import fitz  # PyMuPDF
    PDF_ADVANCED = True
except ImportError:
    PDF_ADVANCED = False
    print("[Document Tools] PyMuPDF not available, using basic PDF")

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[Document Tools] pytesseract/PIL not available")


# =============================================================================
# DOCX OPERATIONS
# =============================================================================

def read_docx(file_path: str) -> str:
    """Read text content from a DOCX file."""
    if not DOCX_AVAILABLE:
        return "Error: python-docx not installed. Run: pip install python-docx"

    try:
        doc = Document(file_path)
        full_text = []

        for para in doc.paragraphs:
            full_text.append(para.text)

        # Include text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text.append(cell.text)

        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading DOCX: {e}"


def write_docx(file_path: str, content: str, title: Optional[str] = None) -> str:
    """Create a new DOCX file with the given content."""
    if not DOCX_AVAILABLE:
        return "Error: python-docx not installed. Run: pip install python-docx"

    try:
        doc = Document()

        if title:
            heading = doc.add_heading(title, level=1)

        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                doc.add_paragraph(para.strip())

        doc.save(file_path)
        return f"Successfully created DOCX: {file_path}"
    except Exception as e:
        return f"Error writing DOCX: {e}"


def docx_to_pdf(docx_path: str, pdf_path: Optional[str] = None) -> str:
    """Convert DOCX to PDF (requires Microsoft Word or LibreOffice)."""
    try:
        if sys.platform == "win32":
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.visible = False

            if not pdf_path:
                pdf_path = docx_path.replace('.docx', '.pdf')

            doc = word.Documents.Open(os.path.abspath(docx_path))
            doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # 17 = PDF
            doc.Close()
            word.Quit()

            return f"Converted to PDF: {pdf_path}"
        else:
            return "PDF conversion requires Windows with MS Word or use LibreOffice"
    except Exception as e:
        return f"Error converting to PDF: {e}"


# =============================================================================
# EXCEL OPERATIONS
# =============================================================================

def read_excel(file_path: str, sheet_name: Optional[str] = None) -> str:
    """Read data from an Excel file and return as formatted text."""
    if not EXCEL_AVAILABLE:
        return "Error: openpyxl/pandas not installed. Run: pip install openpyxl pandas"

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.to_string()
    except Exception as e:
        return f"Error reading Excel: {e}"


def write_excel(file_path: str, data: List[List[Any]], headers: Optional[List[str]] = None) -> str:
    """Write data to an Excel file."""
    if not EXCEL_AVAILABLE:
        return "Error: openpyxl/pandas not installed. Run: pip install openpyxl pandas"

    try:
        wb = openpyxl.Workbook()
        ws = wb.active

        # Add headers if provided
        if headers:
            ws.append(headers)
            # Style headers
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")

        # Add data
        for row in data:
            ws.append(row)

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        wb.save(file_path)
        return f"Successfully created Excel: {file_path}"
    except Exception as e:
        return f"Error writing Excel: {e}"


def excel_to_csv(excel_path: str, csv_path: Optional[str] = None, sheet_name: Optional[str] = None) -> str:
    """Convert Excel file to CSV."""
    if not EXCEL_AVAILABLE:
        return "Error: pandas not installed"

    try:
        if not csv_path:
            csv_path = excel_path.replace('.xlsx', '.csv').replace('.xls', '.csv')

        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df.to_csv(csv_path, index=False)

        return f"Converted to CSV: {csv_path}"
    except Exception as e:
        return f"Error converting to CSV: {e}"


# =============================================================================
# POWERPOINT OPERATIONS
# =============================================================================

def read_pptx(file_path: str) -> str:
    """Extract text from a PowerPoint presentation."""
    if not PPT_AVAILABLE:
        return "Error: python-pptx not installed. Run: pip install python-pptx"

    try:
        prs = Presentation(file_path)
        full_text = []

        for i, slide in enumerate(prs.slides, 1):
            full_text.append(f"\n--- Slide {i} ---")
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    full_text.append(shape.text)

        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading PPTX: {e}"


def create_pptx(file_path: str, slides_data: List[Dict[str, str]]) -> str:
    """Create a PowerPoint presentation.

    Args:
        file_path: Output file path
        slides_data: List of dicts with 'title' and 'content' keys
    """
    if not PPT_AVAILABLE:
        return "Error: python-pptx not installed. Run: pip install python-pptx"

    try:
        prs = Presentation()

        for slide_data in slides_data:
            slide_layout = prs.slide_layouts[1]  # Title and Content layout
            slide = prs.slides.add_slide(slide_layout)

            title = slide.shapes.title
            title.text = slide_data.get('title', 'Untitled Slide')

            content_placeholder = slide.placeholders[1]
            text_frame = content_placeholder.text_frame
            text_frame.text = slide_data.get('content', '')

        prs.save(file_path)
        return f"Successfully created PowerPoint: {file_path} ({len(slides_data)} slides)"
    except Exception as e:
        return f"Error creating PPTX: {e}"


# =============================================================================
# ADVANCED PDF OPERATIONS
# =============================================================================

def extract_pdf_text(file_path: str, pages: Optional[List[int]] = None) -> str:
    """Extract text from PDF with advanced features."""
    if PDF_ADVANCED:
        try:
            doc = fitz.open(file_path)
            text = []

            page_range = pages if pages else range(len(doc))

            for page_num in page_range:
                if page_num < len(doc):
                    page = doc[page_num]
                    text.append(f"\n--- Page {page_num + 1} ---\n")
                    text.append(page.get_text())

            doc.close()
            return "".join(text)
        except Exception as e:
            return f"Error extracting PDF text: {e}"
    else:
        # Fallback to basic PyPDF2
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = []
                page_range = pages if pages else range(len(reader.pages))

                for page_num in page_range:
                    if page_num < len(reader.pages):
                        text.append(f"\n--- Page {page_num + 1} ---\n")
                        text.append(reader.pages[page_num].extract_text())

                return "".join(text)
        except Exception as e:
            return f"Error reading PDF: {e}"


def pdf_to_images(file_path: str, output_folder: str, dpi: int = 150) -> str:
    """Convert PDF pages to images."""
    if not PDF_ADVANCED:
        return "Error: PyMuPDF not installed. Run: pip install PyMuPDF"

    try:
        os.makedirs(output_folder, exist_ok=True)
        doc = fitz.open(file_path)
        image_files = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            output_file = os.path.join(output_folder, f"page_{page_num + 1}.png")
            pix.save(output_file)
            image_files.append(output_file)

        doc.close()
        return f"Converted {len(image_files)} pages to images in: {output_folder}"
    except Exception as e:
        return f"Error converting PDF to images: {e}"


def merge_pdfs(input_files: List[str], output_file: str) -> str:
    """Merge multiple PDF files into one."""
    if not PDF_ADVANCED:
        return "Error: PyMuPDF not installed. Run: pip install PyMuPDF"

    try:
        result = fitz.open()

        for pdf_file in input_files:
            with fitz.open(pdf_file) as doc:
                result.insert_pdf(doc)

        result.save(output_file)
        result.close()

        return f"Merged {len(input_files)} PDFs into: {output_file}"
    except Exception as e:
        return f"Error merging PDFs: {e}"


# =============================================================================
# OCR OPERATIONS
# =============================================================================

def ocr_image(image_path: str, language: str = 'eng') -> str:
    """Extract text from an image using OCR."""
    if not OCR_AVAILABLE:
        return "Error: pytesseract/PIL not installed. Run: pip install pytesseract pillow"

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=language)
        return text.strip()
    except Exception as e:
        return f"Error performing OCR: {e}"


def ocr_pdf(pdf_path: str, output_path: Optional[str] = None, language: str = 'eng') -> str:
    """Perform OCR on a PDF file."""
    if not OCR_AVAILABLE or not PDF_ADVANCED:
        return "Error: Required libraries not installed"

    try:
        # First convert PDF to images
        temp_dir = tempfile.mkdtemp()
        doc = fitz.open(pdf_path)

        all_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap()
            img_path = os.path.join(temp_dir, f"page_{page_num}.png")
            pix.save(img_path)

            # OCR the image
            text = ocr_image(img_path, language)
            all_text.append(f"\n--- Page {page_num + 1} ---\n{text}")

            # Clean up temp image
            os.remove(img_path)

        doc.close()
        os.rmdir(temp_dir)

        result_text = "\n".join(all_text)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result_text)
            return f"OCR completed. Text saved to: {output_path}"

        return result_text
    except Exception as e:
        return f"Error performing PDF OCR: {e}"


def detect_text_in_image(image_path: str) -> Dict[str, Any]:
    """Detect text regions and their content in an image."""
    if not OCR_AVAILABLE:
        return {"error": "pytesseract/PIL not installed"}

    try:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Extract text blocks with confidence
        text_blocks = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60:  # Confidence threshold
                text_blocks.append({
                    'text': data['text'][i],
                    'confidence': data['conf'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i]
                })

        return {
            'blocks': text_blocks,
            'total_blocks': len(text_blocks)
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_document_info(file_path: str) -> Dict[str, Any]:
    """Get metadata and information about a document."""
    info = {
        'file_path': file_path,
        'exists': os.path.exists(file_path),
        'size_bytes': 0,
        'extension': '',
        'type': 'unknown'
    }

    if not os.path.exists(file_path):
        return info

    info['size_bytes'] = os.path.getsize(file_path)
    info['size_mb'] = round(info['size_bytes'] / (1024 * 1024), 2)

    _, ext = os.path.splitext(file_path)
    info['extension'] = ext.lower()

    # Determine document type
    if ext.lower() == '.docx':
        info['type'] = 'Word Document'
        if DOCX_AVAILABLE:
            try:
                doc = Document(file_path)
                info['paragraphs'] = len(doc.paragraphs)
                info['tables'] = len(doc.tables)
            except:
                pass
    elif ext.lower() in ['.xlsx', '.xls']:
        info['type'] = 'Excel Spreadsheet'
        if EXCEL_AVAILABLE:
            try:
                wb = openpyxl.load_workbook(file_path, read_only=True)
                info['sheets'] = wb.sheetnames
                info['sheet_count'] = len(wb.sheetnames)
            except:
                pass
    elif ext.lower() == '.pptx':
        info['type'] = 'PowerPoint Presentation'
        if PPT_AVAILABLE:
            try:
                prs = Presentation(file_path)
                info['slides'] = len(prs.slides)
            except:
                pass
    elif ext.lower() == '.pdf':
        info['type'] = 'PDF Document'
        if PDF_ADVANCED:
            try:
                doc = fitz.open(file_path)
                info['pages'] = len(doc)
                doc.close()
            except:
                pass

    return info


# Export all functions
__all__ = [
    'read_docx', 'write_docx', 'docx_to_pdf',
    'read_excel', 'write_excel', 'excel_to_csv',
    'read_pptx', 'create_pptx',
    'extract_pdf_text', 'pdf_to_images', 'merge_pdfs',
    'ocr_image', 'ocr_pdf', 'detect_text_in_image',
    'get_document_info'
]
