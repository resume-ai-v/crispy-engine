from docx import Document
import io

def text_to_docx_bytes(resume_text):
    doc = Document()
    for line in resume_text.split("\n"):
        doc.add_paragraph(line)
    f = io.BytesIO()
    doc.save(f)
    f.seek(0)
    return f.read()
