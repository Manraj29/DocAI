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

def get_table_extractor():
    return Agent(
        role="Table Extractor",
        goal="Extract tables from document text and present them in a structured format",
        backstory="You scan the text and convert any found tables into rows and columns in JSON format.",
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )
