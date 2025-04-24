from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def text_to_pdf_bytes(text: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    text_lines = text.split('\n')
    y = height - 40
    for line in text_lines:
        pdf.drawString(40, y, line.strip())
        y -= 14
        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)
    return buffer.read()
