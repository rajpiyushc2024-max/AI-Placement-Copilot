import pymupdf
from docx import Document


def extract_pdf_text(file):
    text = ""

    pdf = pymupdf.open(
        stream=file.read(),
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


def extract_docx_text(file):
    document = Document(file)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


def extract_text(file):

    file_name = file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(file)

    elif file_name.endswith(".docx"):
        return extract_docx_text(file)

    else:
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )