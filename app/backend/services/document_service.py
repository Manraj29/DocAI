import os
import tempfile
from backend.document_parser import file_preprocess, extract_images_from_pdf, extract_text_from_image
from backend.cleaner import clean_text_with_gemini, clean_ocr_text_with_gemini
import base64
from io import BytesIO

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


def process_document(file_bytes, filename):
    ext = filename.split(".")[-1].lower()
    if ext == "docx":
        file_bytes = convert_to_pdf(file_bytes, ext)
        ext = "pdf"
    extracted_text = file_preprocess(file_bytes, ext)
    cleaned_text = clean_text_with_gemini(extracted_text)

    images = extract_images_from_pdf(file_bytes) if ext == "pdf" else []
    img_ocr = []
    img_corrected = []

    images_b64 = []  # Will hold base64 encoded strings of images

    for img in images:
        # Convert img (PIL Image or raw bytes) to base64 string
        if hasattr(img, "save"):  # likely a PIL Image
            buffered = BytesIO()
            img.save(buffered, format="PNG")  # or JPEG if appropriate
            img_bytes = buffered.getvalue()
        else:
            img_bytes = img  # already bytes?

        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images_b64.append(img_b64)

        ocr_text = extract_text_from_image(img)
        cleaned = clean_ocr_text_with_gemini(ocr_text, img)
        img_ocr.append(ocr_text)
        img_corrected.append(cleaned)

    return {
        "extracted_text": extracted_text,
        "cleaned_text": cleaned_text,
        "images": images_b64,  # <-- base64 encoded strings!
        "img_ocr": img_ocr,
        "img_correct_ocr": img_corrected,
        "extension": ext,
        "filename": filename,
        "file_bytes": base64.b64encode(file_bytes).decode("utf-8") 
    }
