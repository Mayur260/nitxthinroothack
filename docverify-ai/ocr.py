"""
ocr.py
------
Text extraction from uploaded documents.

Currently returns placeholder text.  When you're ready to add real OCR:

  Option A – Tesseract (free, local):
    pip install pytesseract pillow
    Also install the Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki

  Option B – Google Cloud Vision (cloud, more accurate):
    pip install google-cloud-vision

  Option C – AWS Textract (cloud, great for forms):
    pip install boto3

See the TODO comments in extract_text() for drop-in code snippets.
"""


def extract_text(file_bytes: bytes, content_type: str) -> str:
    """
    Extract plain text from a document.

    Args:
        file_bytes:   Raw bytes of the file.
        content_type: MIME type of the file.

    Returns:
        Extracted text as a string.
    """
    if content_type == "application/pdf":
        return _extract_from_pdf(file_bytes)
    elif content_type.startswith("image/"):
        return _extract_from_image(file_bytes, content_type)
    else:
        return "(Unsupported file type for OCR)"


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_from_image(file_bytes: bytes, content_type: str) -> str:
    """
    Extract text from an image file using OCR.

    TODO — swap the placeholder with real Tesseract OCR:

        from PIL import Image
        import pytesseract, io

        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img)
    """
    return _placeholder_text("image")


def _extract_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file.

    TODO — swap the placeholder with PyMuPDF (fitz):

        import fitz  # pip install pymupdf

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        return "\n\n--- Page Break ---\n\n".join(pages)

    Or with pdfplumber:

        import pdfplumber, io

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    """
    return _placeholder_text("pdf")


def _placeholder_text(source: str) -> str:
    """Return realistic-looking placeholder OCR output."""
    return (
        f"[OCR placeholder – {source} detected]\n\n"
        "INVOICE #INV-2024-0847\n\n"
        "Date: March 15, 2024\n"
        "Due Date: April 15, 2024\n\n"
        "BILL TO:\n"
        "Acme Corporation\n"
        "123 Business Street\n"
        "San Francisco, CA 94102\n\n"
        "ITEMS:\n"
        "Professional Services  –  $5,000.00\n"
        "Consulting Fee         –  $3,500.00\n\n"
        "SUBTOTAL: $8,500.00\n"
        "TAX (0%): $0.00\n"
        "TOTAL: $8,500.00\n\n"
        "Payment Terms: Net 30\n"
        "Account Number: 4532-8901-2347\n\n"
        "Authorised Signature: _______________\n"
        "Company Stamp: [STAMP AREA]"
    )
