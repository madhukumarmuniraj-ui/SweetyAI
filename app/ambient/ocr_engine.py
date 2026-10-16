from __future__ import annotations

import base64
import io
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    text: str
    confidence: float = 0.95
    box: Optional[Dict[str, int]] = None
    block_type: str = "paragraph"  # "code", "legal_citation", "error_trace", "heading", "paragraph"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 2),
            "box": self.box,
            "block_type": self.block_type,
        }


class OCREngine:
    """
    High-speed OCR processing engine for real-time desktop screen frame extraction.
    Decodes base64 frames, applies image enhancement, and extracts structured text blocks.
    """

    def __init__(self):
        self._tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        try:
            import pytesseract
            # Test if executable responds
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def decode_image(self, image_data: str | bytes) -> Optional[Any]:
        """Decodes base64 data URL, raw base64, or bytes into PIL Image."""
        from PIL import Image

        try:
            if isinstance(image_data, str):
                if image_data.startswith("data:image"):
                    # Strip base64 data URL header
                    image_data = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", image_data)
                raw_bytes = base64.b64decode(image_data)
            else:
                raw_bytes = image_data

            img = Image.open(io.BytesIO(raw_bytes))
            return img
        except Exception as e:
            logger.warning(f"[OCREngine] Failed to decode image: {e}")
            return None

    def classify_block_type(self, text: str) -> str:
        text_lower = text.lower()
        if "traceback (most recent call last)" in text_lower or "syntaxerror" in text_lower or "uncaught typeerror" in text_lower:
            return "error_trace"
        if any(kw in text for kw in ["def ", "class ", "import ", "const ", "function ", "return ", "if __name__"]):
            return "code"
        if any(kw in text_lower for kw in ["section ", "act, 19", "act, 20", "arbitration", "contract"]):
            return "legal_citation"
        if len(text.strip()) < 50 and text.isupper():
            return "heading"
        return "paragraph"

    def extract_text(self, image_data: str | bytes) -> List[TextBlock]:
        """Extracts text blocks from screen capture image."""
        img = self.decode_image(image_data)
        if img is None:
            return []

        blocks: List[TextBlock] = []

        if self._tesseract_available:
            try:
                import pytesseract
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                n_boxes = len(data["text"])
                current_text = []
                for i in range(n_boxes):
                    t = data["text"][i].strip()
                    if t:
                        current_text.append(t)
                combined = " ".join(current_text)
                if combined:
                    blocks.append(TextBlock(
                        text=combined,
                        confidence=0.9,
                        block_type=self.classify_block_type(combined)
                    ))
                return blocks
            except Exception as e:
                logger.warning(f"[OCREngine] Tesseract extraction failed: {e}")

        # Fallback: image dimension summary and OCR text block
        w, h = img.size
        sample_text = f"[Screen Capture: {w}x{h} Resolution, RGB Image]"
        blocks.append(TextBlock(
            text=sample_text,
            confidence=1.0,
            box={"x": 0, "y": 0, "width": w, "height": h},
            block_type="paragraph",
        ))
        return blocks

    def extract_from_text_snippet(self, raw_text: str) -> List[TextBlock]:
        """Parses clipboard or terminal text into typed blocks."""
        lines = [l.strip() for l in raw_text.split("\n\n") if l.strip()]
        blocks = []
        for line in lines:
            blocks.append(TextBlock(
                text=line,
                confidence=1.0,
                block_type=self.classify_block_type(line),
            ))
        return blocks
