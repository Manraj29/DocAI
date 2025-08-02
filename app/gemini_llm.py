import google.generativeai as genai
from dotenv import load_dotenv
import os
from crewai_tools import GeminiTool

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not found in environment.")

class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = model
        self.client = genai.GenerativeModel(self.model)

    def __call__(self, prompt: str) -> str:
        try:
            response = self.client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"[Gemini Error] {str(e)}"

    def invoke(self, prompt: str) -> str:
        return self.__call__(prompt)
