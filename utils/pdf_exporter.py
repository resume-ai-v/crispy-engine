from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def text_to_pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    lines = text.splitlines()

    y = 750
    for line in lines:
        c.drawString(30, y, line)
        y -= 15
        if y < 40:
            c.showPage()
            y = 750
    c.save()
    buffer.seek(0)
    return buffer.read()
