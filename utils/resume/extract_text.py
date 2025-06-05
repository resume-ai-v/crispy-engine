import io
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document

def extract_text_from_file(file_obj, filename):
    filename = filename.lower()
    if filename.endswith(".pdf"):
        return extract_pdf_text(file_obj)
    elif filename.endswith(".docx"):
        doc = Document(file_obj)
        return "\n".join([para.text for para in doc.paragraphs])
    elif filename.endswith(".txt"):
        return file_obj.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format! Upload PDF, DOCX, or TXT.")
