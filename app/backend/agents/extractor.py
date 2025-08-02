from crewai import Agent
from dotenv import load_dotenv
from crewai import Agent, LLM
from dotenv import load_dotenv
import os

load_dotenv()

llm = LLM(
    model=os.getenv("GEMINI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

def get_field_extractor():
    return Agent(
        role="Key-Value Field Extractor",
        goal="Extract structured fields from cleaned document text",
        backstory="You analyze the cleaned text and extract key fields like date, sender, receiver, amount, etc. in JSON format.",
        llm=llm,
        verbose=True
    )
