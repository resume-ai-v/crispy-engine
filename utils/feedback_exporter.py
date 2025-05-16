# utils/feedback_exporter.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


def generate_feedback_pdf(feedback_text: str, user_name="Candidate") -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"{user_name}'s AI Interview Feedback Report")

    c.setFont("Helvetica", 12)
    y = 720
    for line in feedback_text.splitlines():
        c.drawString(40, y, line.strip())
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    buffer.seek(0)
    return buffer.read()
