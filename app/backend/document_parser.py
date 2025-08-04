import base64
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import markdown
import pytesseract
from PIL import Image
import io

import win32com

pytesseract.pytesseract.tesseract_cmd = r"D:\Apps\Tesseract\tesseract.exe"

def convert_to_pdf(file, extension):
    try:
        if extension == "docx":
            import win32com.client as win32

            # Save to temp file if input is bytes
            if isinstance(file, bytes):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                    temp_docx.write(file)
                    temp_docx_path = temp_docx.name
            else:
                temp_docx_path = file

            # Convert using MS Word
            word = win32.Dispatch("Word.Application")
            doc = word.Documents.Open(temp_docx_path)
            pdf_path = temp_docx_path.replace(".docx", ".pdf")
            doc.SaveAs(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
            word.Quit()

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            # Clean up temp files
            os.remove(temp_docx_path)
            os.remove(pdf_path)

            return pdf_bytes

    except Exception as e:
        return f"Error converting {extension} to PDF: {e}"


def file_preprocess(file, selected_extension=None):
    final_text = ""

    if selected_extension == "pdf":
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(file)
                temp_pdf_path = temp_pdf.name

            loader = PyPDFLoader(temp_pdf_path)
            pages = loader.load_and_split()
            for text in pages:
                final_text += text.page_content.strip() + "\n"
        except Exception as e:
            return "Error loading PDF: " + str(e)
        return final_text.strip() if final_text.strip() else "No text found."

    elif selected_extension == "txt":
        try:
            with open(file, "r", encoding="utf-8") as f:
                final_text = f.read().strip()
        except Exception as e:
            return "Error loading TXT: " + str(e)
        return final_text if final_text else "No text found."

    elif selected_extension == "docx":
        pdf_bytes = convert_to_pdf(file, "docx")
        if isinstance(pdf_bytes, bytes):
            return file_preprocess(pdf_bytes, selected_extension="pdf")
        else:
            return pdf_bytes  # error message string

    elif selected_extension == "pptx":
        try:
            import comtypes.client
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            powerpoint.Visible = 1
            deck = powerpoint.Presentations.Open(file)
            pdf_file = file.replace(".pptx", ".pdf")
            deck.SaveAs(pdf_file, 32)  # 32 = PDF format
            deck.Close()
            powerpoint.Quit()
            return file_preprocess(pdf_file, "pdf")
        except Exception as e:
            return "Error loading PPTX: " + str(e)

    elif selected_extension in ["jpg", "jpeg", "png"]:
        try:
            if isinstance(file, bytes):
                image = Image.open(io.BytesIO(file))
            else:
                image = Image.open(file)
            text = pytesseract.image_to_string(image).strip()
            return text if text else "No text found."
        except Exception as e:
            return f"[OCR Image Error]: {str(e)}"

    else:
        raise ValueError("Invalid file extension selected.")

def extract_images_from_pdf(file_bytes):
    pdf = PdfReader(io.BytesIO(file_bytes))
    images = []

    for page_index, page in enumerate(pdf.pages):
        try:
            if hasattr(page, "images"):
                for img_index, img_dict in enumerate(page.images):
                    image_bytes = img_dict.data
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        images.append(buffered.getvalue())
                    except Exception as e:
                        print(f"[Image error on page {page_index}]: {e}")
        except Exception as e:
            print(f"[PDF page error at index {page_index}]: {e}")
    return images


def extract_text_from_image(image_path_or_bytes):
    try:
        if isinstance(image_path_or_bytes, bytes):
            image = Image.open(io.BytesIO(image_path_or_bytes))
        else:
            image = Image.open(image_path_or_bytes)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"[OCR Image Error] {str(e)}"
    

def pdf_embed_html(file_bytes: bytes) -> str:
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    return f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="750" type="application/pdf">'

def displayFile(file_path_or_bytes, selected_extension=None):
    try:
        if selected_extension == "pdf":
            if isinstance(file_path_or_bytes, str):
                with open(file_path_or_bytes, "rb") as f:
                    file_bytes = f.read()
            else:
                file_bytes = file_path_or_bytes
            return pdf_embed_html(file_bytes)

        elif selected_extension == "txt":
            if isinstance(file_path_or_bytes, str):
                with open(file_path_or_bytes, "r", encoding="utf-8") as f:
                    text = f.read()
            else:
                text = file_path_or_bytes.decode("utf-8")

            return text.strip()

        elif selected_extension == "docx":
            pdf_bytes = convert_to_pdf(file_path_or_bytes, "docx")
            if isinstance(pdf_bytes, bytes):
                return pdf_embed_html(pdf_bytes)
            else:
                return pdf_bytes

        elif selected_extension == "pptx":
            try:
                import win32com.client as win32
            except ImportError:
                return "win32com module not found. PPTX rendering requires Windows and pywin32."

            source = os.path.abspath(file_path_or_bytes)
            destination = source + ".pdf"

            powerpoint = win32.Dispatch("Powerpoint.Application")
            deck = powerpoint.Presentations.Open(source, WithWindow=False)
            deck.SaveAs(destination, 32)  # 32 = PDF format
            deck.Close()
            powerpoint.Quit()

            with open(destination, "rb") as f:
                file_bytes = f.read()
            return pdf_embed_html(file_bytes)

        else:
            return f"Unsupported file type: {selected_extension}"

    except Exception as e:
        return f"Error displaying file: {e}"
