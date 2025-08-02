from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.rag_service import build_rag_chain_cached

router = APIRouter()

qa_chain = None  # Stored across questions

class QAInput(BaseModel):
    document_text: str
    question: str

@router.post("/")
def ask_question(input_data: QAInput):
    global qa_chain
    if not qa_chain:
        qa_chain = build_rag_chain_cached(input_data.document_text)
    result = qa_chain(input_data.question)
    return {
        "answer": result["result"],
        "context": [doc.page_content for doc in result["source_documents"]]
    }
