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

def get_rule_checker():
    return Agent(
        role="Document Rule Validator",
        goal="Check if a given document satisfies a list of logical validation rules and return a clear validation result.",
        backstory=("""
            You're a precision-focused AI validator that ensures documents comply with structural and content-based rules.
                   
            Given:
            - A document (as plain text)
            - A list of validation rules

            Each rule is in a format like:
            - must_contain: field_name
            - must_have_date
            - if_present: X -> must_contain: Y

            You should return a validation report as JSON, like this:
            {
            "results": [
                {"rule": "...", "status": "pass" or "fail", "reason": "..."},
                ...
            ],
            "overall_validity": VALID or INVALID
            }

            Example format:
            {
            "results": [
                {"rule": "must_contain: date", "status": "pass", "reason": "..."},
                {"rule": "must_contain: date", "status": "pass", "reason": "..."},
                {"rule": "must_have_amount", "status": "fail", "reason": "..."}
            ],
            "overall_validity": VALID,
            "failed rules": [
                {"rule": "must_have_amount", "status": "fail", "reason": "..."}
            ]
            }

            DO NOT return markdown or wrap JSON in backticks. Only return the JSON. Do not add any explainations or additional text, just return the JSON.
        """),
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )

# **IMPORTANT:**
#             - Consider the document VALID only if*at least 60% of the rules PASS.
#             - Count the total number of rules, then how many passed.
#             - If (passed / total) >= 0.6, return `overall_validity: VALID`, else INVALID.