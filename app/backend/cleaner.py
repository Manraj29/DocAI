import io
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not found in environment.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

def clean_text_with_gemini(raw_text: str) -> str:
    if not raw_text.strip():
        return "No text provided."

    prompt = f"""
        You are an text cleaner.
        The following text has been extracted from a document. It contains formatting issues, broken lines, and possibly incorrect characters. Please clean it up, fix spelling mistakes, and format it into a readable version. Do not hallucinate content. Do not add any additional information. Just return the cleaned text. Do not make any changes.
        Extracted text:
        {raw_text}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Cleanup Error] {str(e)}"

def clean_ocr_text_with_gemini(ocr_text, image_bytes):
    if not ocr_text.strip():
        return "no text "
    if isinstance(image_bytes, bytes):
        image = Image.open(io.BytesIO(image_bytes))
    else:
        image = Image.open(image_bytes)

    text = f"""
        You are a text cleaner.
        The following text has been extracted from an image using OCR. It might not be proper so please refine and correct it. Do not hallucinate content. Do not add any additional information. Just return the text you see in the image. Do not make any changes. 
        Extracted text:
        {ocr_text}
    """

    response = model.generate_content([text, image])
    response.resolve()
    return response.text