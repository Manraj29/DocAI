import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def validate_document(input):
    prompt = f"""
    You are a strict document validator. The following text is from a document:

    ---
    {input.text}
    ---

    The user wants to validate it with the following rules:
    {input.rules}

    Go through each rule and check if it is satisfied in the document.
    Return a JSON like this:
    {{
      "results": [
        {{"rule": "...", "status": "pass" or "fail", "reason": "..." }},
        ...
      ],
      "overall_validity": VALID or INVALID,
        "failed rules": [
            {{"rule": "...", "status": "fail", "reason": "..."}}
        ]
    }}

    Only return raw JSON. Do not include explanations or wrap in code block.
    """

    response = model.generate_content(prompt)
    result_text = response.text.strip()

    # Remove ```json or ``` if it's there
    result_text = re.sub(r"^```(?:json)?\n", "", result_text)
    result_text = re.sub(r"\n```$", "", result_text)

    try:
        return json.loads(result_text)
    except Exception as e:
        return {
            "error": "Could not parse model response as JSON.",
            "raw": result_text,
            "exception": str(e)
        }
