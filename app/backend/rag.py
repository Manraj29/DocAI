# rag_engine.py

import os
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import LLMResult
from langchain.llms.base import LLM
from typing import List, Optional
import google.generativeai as genai
from pydantic import PrivateAttr

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiLLM(LLM):
    """LangChain-compatible wrapper around Google Gemini Pro."""

    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.2
    _model: any = PrivateAttr()

    def __init__(self, model_name="gemini-1.5-flash", temperature=0.2, **kwargs):
        super().__init__(model_name=model_name, temperature=temperature, **kwargs)
        self._model = genai.GenerativeModel(model_name)

    @property
    def _llm_type(self) -> str:
        return "gemini-1.5-flash"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        try:
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"(Gemini API error: {e})"

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        generations = []
        for prompt in prompts:
            try:
                response = self._model.generate_content(prompt)
                generations.append([{"text": response.text.strip()}])
            except Exception as e:
                generations.append([{"text": f"(Gemini API error: {e})"}])
        return LLMResult(generations=generations)
    

def build_rag_chain(document_text: str):
    """Builds a Retrieval-Augmented Generation (RAG) chain using HuggingFace embeddings + Gemini Pro."""

    # Step 1: Split document
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(document_text)

    if not chunks:
        raise ValueError("Document could not be split into chunks.")

    # Step 2: Embed chunks with Hugging Face
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

    # Step 3: Use Gemini Pro LLM
    llm = GeminiLLM(temperature=0.2)

    # Step 4: Build retrieval-based QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 1}),
        return_source_documents=True
    )

    return qa_chain
