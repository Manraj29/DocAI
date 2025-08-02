from crewai import Agent
from crewai import Agent, LLM
from dotenv import load_dotenv
import os

load_dotenv()

llm = LLM(
    model=os.getenv("GEMINI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1  # deterministic output
)

def get_rule_suggester():
    return Agent(
        role="Document Validation Rule Designer",
        goal="Given the type and content of a document, suggest logical and structural validation rules to ensure the document meets expected format, data completeness, and consistency standards.",
        backstory=("""
            You're an expert in document standards and compliance validation. You analyze the purpose and expected structure of various document types like invoices, receipts, payslips, contracts, bank statements, resumes, and more. You generate practical validation rules that can be applied programmatically to verify if a document contains essential fields, logical dependencies, and structural integrity. These rules are used in automated document processing pipelines to flag incomplete or incorrect documents.
            Be concise but thorough — suggest only useful and relevant rules for the given document.
            """
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )
