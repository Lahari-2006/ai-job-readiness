"""
PDF Extraction Service
Uses pdfplumber to extract plain text from PDF files.
Supports both UploadFile (FastAPI) and raw bytes input.
"""

import io
import logging
import pdfplumber
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


async def extract_text_from_pdf_upload(file: UploadFile) -> str:
    """
    Extract all text from an uploaded PDF file.

    Args:
        file: FastAPI UploadFile (PDF)

    Returns:
        str: Extracted plain text
    """
    try:
        # Read uploaded bytes
        file_bytes = await file.read()
        text = extract_text_from_bytes(file_bytes)
        await file.seek(0)  # Reset pointer for potential re-use
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Could not extract text from PDF '{file.filename}'. Ensure it is a valid, non-encrypted PDF.",
        )


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from raw PDF bytes.

    Args:
        pdf_bytes: Raw bytes of the PDF

    Returns:
        str: Concatenated text from all pages
    """
    all_text = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                all_text.append(page_text.strip())
            else:
                logger.warning(f"Page {page_num} returned no text (possibly scanned image).")

    if not all_text:
        raise ValueError("No text could be extracted. The PDF may be image-based or empty.")

    return "\n".join(all_text)


def clean_text(text: str) -> str:
    """
    Basic text cleanup — removes excessive whitespace and special characters.
    Used before sending text to AWS Comprehend.

    Args:
        text: Raw extracted text

    Returns:
        str: Cleaned text
    """
    import re
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    # Remove non-ASCII characters (optional — Comprehend handles Unicode well)
    text = text.encode("ascii", errors="ignore").decode()
    return text.strip()
