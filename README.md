# 🧠 DocAI: Document Validation System

**DocuIntel** is an intelligent document processing pipeline that leverages GenAI and traditional NLP to extract, classify, validate, and answer questions about documents. It supports multiple file types (PDF, DOCX, TXT, JPG, PNG), integrates AI agents for field extraction and rule validation, and provides a streamlined UI for interaction, query handling, and results visualization.

---

## Features

- Supports multiple document formats: `.pdf`, `.docx`, `.txt`, `.jpg`, `.png`
- Extracts text and tables using NLP and OCR (for images)
- Uses Google Gemini API + CrewAI agents for intelligent:
  - Document classification
  - Key-value field extraction
  - Table extraction
  - AI-generated validation rule suggestions
  - Rule satisfaction checking
- Custom rule input support by user for AI-based validation
- Query interface powered by RAG pipeline (MiniLM + Gemini API)
- MongoDB storage for structured document results
- Interactive front-end using Streamlit
- Backend APIs via Flask + FastAPI

---

## Tech Stack

| Layer       | Tech/Tool                                   |
|------------|----------------------------------------------|
| Frontend   | [Streamlit](https://streamlit.io/)           |
| Backend    | [Flask](https://flask.palletsprojects.com/) + [FastAPI](https://fastapi.tiangolo.com/) |
| Embeddings | `all-MiniLM-L6-v2` from HuggingFace          |
| LLM        | Google Gemini API                            |
| Vector DB  | [FAISS](https://github.com/facebookresearch/faiss) |
| OCR        | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) |
| AI Agents  | [CrewAI](https://docs.crewai.com/)           |
| Database   | MongoDB                                      |

---

## Architecture Overview
### 1. Document Upload
- Users can upload documents via the Streamlit UI.
- Files are parsed based on type (PDF, DOCX, Image, etc.).
- OCR is applied to images for text extraction.
### 2. Preprocessing & Cleaning
- Text is cleaned via Gemini API for better understanding.
- Image-based text is verified by Gemini API.
### 3. Agentic AI via CrewAI
- **Classifier Agent**: Classifies the document type.
- **Field Extractor Agent**: Extracts key-value pairs.
- **Table Extractor Agent**: Extracts structured tables.
- **Rule Suggestor Agent**: Suggests AI-based logical validation rules.
- **Rule Checker Agent**: Checks rule satisfaction and marks document as Valid/Invalid (>=60% rules must pass).
### 4. Custom Rule Validation
- Users can enter their own rules in natural language.
- Gemini validates the custom rules against the document text.
### 5. RAG-based Question Answering
- Implemented with Huggingface MiniLM embeddings + FAISS + Gemini.
- Users can ask contextual questions about the document.
### 6. Storage
- Final results (classification, fields, tables, rules, QA answers, etc.) are stored in MongoDB.

---

## Example Use Cases
1. Invoice validation with AI-generated and custom rules
2. Resume parsing and structure validation
3. Identity document classification + key field extraction
4. Business receipts table extraction
5. Ask natural questions from document contents

---

## Screenshots
Uploading Document
<img width="1919" height="985" alt="image" src="https://github.com/user-attachments/assets/f517c674-1cee-4f0e-b756-e39217f09eb3" />
Get Insights like images, key-value pairs, tables from the document
<img width="1808" height="930" alt="image" src="https://github.com/user-attachments/assets/2abfe357-88df-48df-888b-4466ea6e034f" />
<img width="1759" height="926" alt="image" src="https://github.com/user-attachments/assets/a0b576ef-b783-40d5-baec-0647d61e979c" />
<img width="1779" height="922" alt="image" src="https://github.com/user-attachments/assets/9495463a-0f77-44a4-8419-4f0b14493d61" />
User Querying
<img width="1775" height="443" alt="image" src="https://github.com/user-attachments/assets/23d1e809-d0c4-4501-aefe-751188e97e32" />
AI generated Rule Validation
<img width="1782" height="429" alt="image" src="https://github.com/user-attachments/assets/923d28a7-0fe3-4400-8a77-e6ef86c30e45" />
<img width="1753" height="758" alt="image" src="https://github.com/user-attachments/assets/e5eccdd2-ac1f-4fae-b1c0-a7590b955d28" />
Custom rule validation
<img width="1770" height="918" alt="image" src="https://github.com/user-attachments/assets/d21c937a-c782-43a2-af51-f6f7f65eb211" />
Storing data to MongoDB Database
<img width="505" height="230" alt="image" src="https://github.com/user-attachments/assets/1dd38035-f643-4b0c-831b-4bbfb393cbf2" />
<img width="694" height="764" alt="image" src="https://github.com/user-attachments/assets/80a025c9-3638-4822-bb0c-6738bb9c090a" />

---

Developed by Manraj Singh Virdi

