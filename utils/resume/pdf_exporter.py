import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def text_to_pdf_bytes(text: str) -> bytes:
    """
    Converts raw text into a PDF and returns it as byte content.

    Args:
        text (str): Resume or content to embed in PDF

    Returns:
        bytes: Byte stream of the generated PDF
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin

    for line in text.splitlines():
        c.drawString(margin, y, line[:120])  # Avoids text overflow
        y -= 15
        if y < margin:
            c.showPage()
            y = height - margin

    c.save()
    buffer.seek(0)
    return buffer.read()


def text_to_pdf_file(text: str, filename: str = "document.pdf") -> str:
    """
    Saves PDF content to a .pdf file locally.

    Args:
        text (str): Content to embed
        filename (str): Output path

    Returns:
        str: File path of saved PDF
    """
    pdf_bytes = text_to_pdf_bytes(text)
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
    return filename
