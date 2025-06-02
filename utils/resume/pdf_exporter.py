import os
from fpdf import FPDF

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")

class PdfResumeExporter:
    def __init__(self, resume_text):
        self.resume_text = resume_text

    def export_pdf_bytes(self):
        pdf = FPDF()
        pdf.add_page()
        if not os.path.isfile(FONT_PATH):
            print(f"WARNING: Font file not found at {FONT_PATH}. Falling back to Arial.")
            pdf.set_font("Arial", size=12)
        else:
            pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
            pdf.set_font("DejaVu", size=12)
        for line in self.resume_text.splitlines():
            pdf.cell(0, 10, line, ln=True)
        return pdf.output(dest='S').encode('latin1')

def text_to_pdf_bytes(resume_text):
    return PdfResumeExporter(resume_text).export_pdf_bytes()
