import fitz  # PyMuPDF
import re

def clean_text(text):
    """Light cleanup: remove zero-width spaces and collapse excessive whitespace."""
    text = text.replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from every page of a PDF.
    Returns a list of dicts: {"text": ..., "source": filename, "page": page_number}
    """
    doc = fitz.open(pdf_path)
    filename = pdf_path.split("\\")[-1].split("/")[-1]

    pages_data = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = clean_text(page.get_text())
        if text:
            pages_data.append({
                "text": text,
                "source": filename,
                "page": page_num + 1
            })
    doc.close()

    if not pages_data:
        print(f"Warning: no extractable text found in {filename}")

    return pages_data