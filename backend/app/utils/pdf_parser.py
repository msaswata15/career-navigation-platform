import PyPDF2
import docx
import io

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX"""
    if filename.endswith('.pdf'):
        return _extract_from_pdf(file_bytes)
    elif filename.endswith('.docx'):
        return _extract_from_docx(file_bytes)
    else:
        return file_bytes.decode('utf-8')

def _extract_from_pdf(file_bytes: bytes) -> str:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def _extract_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])
