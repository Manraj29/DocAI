from crewai import Agent
from textwrap import dedent
from crewai import Agent, LLM
from dotenv import load_dotenv
import os

load_dotenv()

llm = LLM(
    model=os.getenv("GEMINI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1  # deterministic output
)

def get_document_classifier():
    return Agent(
        role="Document Type Classifier",
        goal="Classify the type of document accurately",
        backstory="You are trained to analyze and categorize documents into types like Invoice, Receipt, Payslip, Bank Statement, Legal agreements (NDAs, contracts, MoUs), Resumes/CVs, Research papers, Compliance forms, Business proposals, Insurance policies, Meeting minutes or any other kindoff document etc.",
        verbose=True,
        llm=llm,
    )
