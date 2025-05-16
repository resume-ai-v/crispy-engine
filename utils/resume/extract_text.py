from PyPDF2 import PdfReader
import docx
import io

def extract_text_from_file(file_obj, filename=None) -> str:
    """
    Extracts raw text from PDF or DOCX file-like object.

    Args:
        file_obj (BytesIO/File): File stream (from UploadFile or open())
        filename (str): Optional filename (used for type detection)

    Returns:
        str: Extracted plain text
    """
    try:
        ext = filename or getattr(file_obj, "name", "")
        ext = ext.lower()

        if ext.endswith(".pdf"):
            return _extract_pdf(file_obj)
        elif ext.endswith(".docx"):
            return _extract_docx(file_obj)
        else:
            raise ValueError("Unsupported file type.")
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
        return ""


def _extract_pdf(file_obj) -> str:
    if isinstance(file_obj, bytes):
        file_obj = io.BytesIO(file_obj)
    reader = PdfReader(file_obj)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])


def _extract_docx(file_obj) -> str:
    if isinstance(file_obj, bytes):
        file_obj = io.BytesIO(file_obj)
    doc = docx.Document(file_obj)
    return "\n".join([para.text for para in doc.paragraphs])
