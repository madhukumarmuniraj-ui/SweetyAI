"""
SweetyAI Image Generation & Editing Tools
Stable Diffusion, PIL/OpenCV for image manipulation
"""

import os
from typing import Tuple, List, Optional, Dict, Any
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[Image Tools] PIL/Pillow not available. Run: pip install pillow")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[Image Tools] OpenCV not available. Run: pip install opencv-python")

try:
    from diffusers import StableDiffusionPipeline
    import torch
    STABLE_DIFFUSION_AVAILABLE = True
except ImportError:
    STABLE_DIFFUSION_AVAILABLE = False
    print("[Image Tools] Stable Diffusion not available. Run: pip install diffusers transformers accelerate")


# =============================================================================
# IMAGE GENERATION (STABLE DIFFUSION)
# =============================================================================

_sd_pipeline = None

def load_stable_diffusion(model_id: str = "runwayml/stable-diffusion-v1-5") -> str:
    """Load Stable Diffusion model (first time may take a while)."""
    if not STABLE_DIFFUSION_AVAILABLE:
        return "Error: diffusers not installed"

    global _sd_pipeline
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _sd_pipeline = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        return f"Stable Diffusion loaded on {device}"
    except Exception as e:
        return f"Error loading Stable Diffusion: {e}"


def generate_image(
    prompt: str,
    output_path: str,
    negative_prompt: Optional[str] = None,
    width: int = 512,
    height: int = 512,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5
) -> str:
    """Generate an image using Stable Diffusion."""
    if not STABLE_DIFFUSION_AVAILABLE:
        return "Error: Stable Diffusion not available"

    global _sd_pipeline
    if _sd_pipeline is None:
        load_result = load_stable_diffusion()
        if "Error" in load_result:
            return load_result

    try:
        image = _sd_pipeline(
            prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        ).images[0]

        image.save(output_path)
        return f"Image generated: {output_path}"
    except Exception as e:
        return f"Error generating image: {e}"


# =============================================================================
# BASIC IMAGE EDITING (PIL)
# =============================================================================

def resize_image(input_path: str, output_path: str, width: int, height: int) -> str:
    """Resize an image."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        resized.save(output_path)
        return f"Image resized to {width}x{height}: {output_path}"
    except Exception as e:
        return f"Error resizing image: {e}"


def crop_image(input_path: str, output_path: str, left: int, top: int, right: int, bottom: int) -> str:
    """Crop an image."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)
        cropped = img.crop((left, top, right, bottom))
        cropped.save(output_path)
        return f"Image cropped: {output_path}"
    except Exception as e:
        return f"Error cropping image: {e}"


def rotate_image(input_path: str, output_path: str, angle: float, expand: bool = True) -> str:
    """Rotate an image."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)
        rotated = img.rotate(angle, expand=expand)
        rotated.save(output_path)
        return f"Image rotated {angle}°: {output_path}"
    except Exception as e:
        return f"Error rotating image: {e}"


def apply_filter(input_path: str, output_path: str, filter_name: str) -> str:
    """Apply a filter to an image.

    Filters: blur, contour, detail, edge_enhance, emboss, sharpen, smooth
    """
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    filters = {
        'blur': ImageFilter.BLUR,
        'contour': ImageFilter.CONTOUR,
        'detail': ImageFilter.DETAIL,
        'edge_enhance': ImageFilter.EDGE_ENHANCE,
        'emboss': ImageFilter.EMBOSS,
        'sharpen': ImageFilter.SHARPEN,
        'smooth': ImageFilter.SMOOTH
    }

    try:
        img = Image.open(input_path)
        if filter_name.lower() not in filters:
            return f"Unknown filter. Available: {', '.join(filters.keys())}"

        filtered = img.filter(filters[filter_name.lower()])
        filtered.save(output_path)
        return f"Filter '{filter_name}' applied: {output_path}"
    except Exception as e:
        return f"Error applying filter: {e}"


def adjust_brightness(input_path: str, output_path: str, factor: float) -> str:
    """Adjust image brightness (factor: 0.0=black, 1.0=original, 2.0=twice as bright)."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)
        enhancer = ImageEnhance.Brightness(img)
        enhanced = enhancer.enhance(factor)
        enhanced.save(output_path)
        return f"Brightness adjusted ({factor}x): {output_path}"
    except Exception as e:
        return f"Error adjusting brightness: {e}"


def adjust_contrast(input_path: str, output_path: str, factor: float) -> str:
    """Adjust image contrast."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)
        enhancer = ImageEnhance.Contrast(img)
        enhanced = enhancer.enhance(factor)
        enhanced.save(output_path)
        return f"Contrast adjusted ({factor}x): {output_path}"
    except Exception as e:
        return f"Error adjusting contrast: {e}"


def add_text_to_image(
    input_path: str,
    output_path: str,
    text: str,
    position: Tuple[int, int],
    font_size: int = 40,
    color: Tuple[int, int, int] = (255, 255, 255)
) -> str:
    """Add text overlay to an image."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        draw.text(position, text, fill=color, font=font)
        img.save(output_path)
        return f"Text added: {output_path}"
    except Exception as e:
        return f"Error adding text: {e}"


def convert_image_format(input_path: str, output_path: str, format: str = None) -> str:
    """Convert image to different format (PNG, JPEG, BMP, etc.)."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"

    try:
        img = Image.open(input_path)

        if format is None:
            _, ext = os.path.splitext(output_path)
            format = ext.lstrip('.').upper()

        if img.mode == 'RGBA' and format == 'JPEG':
            img = img.convert('RGB')

        img.save(output_path, format=format)
        return f"Image converted to {format}: {output_path}"
    except Exception as e:
        return f"Error converting image: {e}"


# =============================================================================
# ADVANCED IMAGE PROCESSING (OPENCV)
# =============================================================================

def detect_faces(input_path: str, output_path: Optional[str] = None) -> str:
    """Detect faces in an image."""
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed"

    try:
        img = cv2.imread(input_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if output_path:
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imwrite(output_path, img)
            return f"Detected {len(faces)} faces. Output: {output_path}"

        return f"Detected {len(faces)} faces"
    except Exception as e:
        return f"Error detecting faces: {e}"


def extract_text_from_image(input_path: str) -> str:
    """Extract text from an image using OCR (pytesseract)."""
    if not PIL_AVAILABLE:
        return "Error: PIL not installed"
    try:
        import pytesseract
        img = Image.open(input_path)
        text = pytesseract.image_to_string(img)
        return text if text.strip() else "No text found in image."
    except Exception as e:
        return f"Error extracting text from image (pytesseract required): {e}"


def remove_background(input_path: str, output_path: str, threshold: int = 240) -> str:
    """Simple background removal (works best with solid backgrounds)."""
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed"

    try:
        img = cv2.imread(input_path)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Create mask
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

        # Apply mask
        result = cv2.bitwise_and(img, img, mask=mask)

        # Convert to RGBA for transparency
        b, g, r = cv2.split(result)
        rgba = cv2.merge([r, g, b, mask])

        cv2.imwrite(output_path, rgba)
        return f"Background removed: {output_path}"
    except Exception as e:
        return f"Error removing background: {e}"


def edge_detection(input_path: str, output_path: str, low_threshold: int = 50, high_threshold: int = 150) -> str:
    """Detect edges in an image using Canny algorithm."""
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed"

    try:
        img = cv2.imread(input_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        cv2.imwrite(output_path, edges)
        return f"Edge detection complete: {output_path}"
    except Exception as e:
        return f"Error detecting edges: {e}"


def image_info(input_path: str) -> Dict[str, Any]:
    """Get detailed information about an image."""
    if not PIL_AVAILABLE:
        return {"error": "PIL not installed"}

    try:
        img = Image.open(input_path)

        info = {
            'path': input_path,
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'file_size_bytes': os.path.getsize(input_path),
            'file_size_mb': round(os.path.getsize(input_path) / (1024 * 1024), 2)
        }

        if hasattr(img, 'info'):
            info['metadata'] = img.info

        return info
    except Exception as e:
        return {"error": str(e)}


__all__ = [
    'generate_image', 'load_stable_diffusion',
    'resize_image', 'crop_image', 'rotate_image',
    'apply_filter', 'adjust_brightness', 'adjust_contrast',
    'add_text_to_image', 'convert_image_format',
    'detect_faces', 'extract_text_from_image', 'remove_background', 'edge_detection',
    'image_info'
]