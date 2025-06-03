import fitz
import base64

# Load image and encode it in base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Extract raw text data from pdf
async def extract_pdf_text(pdf_file):
    """Extract text from the first N pages of a PDF using PyMuPDF"""
    pdf_bytes = await pdf_file.read()  
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for i in range(len(doc)):
        page = doc.load_page(i)
        text += page.get_text()
    return text

# Load prompt from files
def load_prompt(filepath : str) -> str:
    question = ""
    with open(filepath) as f:
        question = f.read()

    return question

