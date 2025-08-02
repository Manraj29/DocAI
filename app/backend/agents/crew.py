import re
from .classifier import get_document_classifier
from .extractor import get_field_extractor
from .table import get_table_extractor
from .rules import get_rule_suggester
from .checker import get_rule_checker


from crewai import Crew, Task, Process
from crewai_tools import FileWriterTool, FileReadTool
import os


def read_file(file_path: str) -> str:
    tool = FileReadTool()
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        result = tool._run(file_path=file_path)
        # Ensure the content is decoded as UTF-8
        result = result.encode('utf-8').decode('utf-8')
        cleaned_text = re.sub(r"```[\w]*\n(.*?)```", r"\1", result, flags=re.DOTALL)
        return cleaned_text.strip()
    except UnicodeDecodeError as e:
        print(f"Error reading file {file_path}: {e}")
        raise

def run_crew_pipeline(cleaned_text: str):
    # Agents
    classifier_agent = get_document_classifier()
    field_extractor_agent = get_field_extractor()
    table_extractor_agent = get_table_extractor()
    rule_suggester_agent = get_rule_suggester()
    rule_checker_agent = get_rule_checker()


    # Tasks
    classify_task = Task(
        description=f"Classify this document:\n\n{cleaned_text}",
        expected_output="Invoice, Receipt, Bank Statement, Payslip, Legal agreements (NDAs, contracts, MoUs), Resumes/CVs, Research papers, Compliance forms, Business proposals, Insurance policies, Meeting minutes or Other.",
        agent=classifier_agent,
        output_file="classification_result.txt"
    )

    field_task = Task(
        description=f"Extract key-value fields:\n\n{cleaned_text}",
        expected_output="JSON with all key fields (e.g. date, sender, amount, etc.)",
        agent=field_extractor_agent,
        output_file="fields_result.json"
    )

    table_task = Task(
        description=f"Extract all tables:\n\n{cleaned_text}",
        expected_output="JSON in the format {table1: ..., table2: ...}",
        agent=table_extractor_agent,
        output_file="tables_result.json"
    )

    rule_task = Task(
        description=f"Suggest some logical validation rules:\n\n{cleaned_text}",
        expected_output="List of basic rules like 'amount must be > 0', 'GST number must match regex XYZ', etc. ",
        agent=rule_suggester_agent,
        output_file="rules_result.json"
    )

    rule_check_task = Task(
        description=(
            f"Here is the extracted document:\n---\n{cleaned_text}\n---\n\n"
            # give rhe rules from previous task
            f"And below are the rules that this document must satisfy, it is the output of the previous task."
            f"Please validate the document against the rules. "
            f"For each rule, say whether it passed or failed, and explain why. "
            f"DO NOT return markdown or wrap JSON in backticks. Only return the JSON. Do not add any explainations or additional text, just return the JSON."
            f"Return the result in JSON format with individual rule status and an overall 'VALID' or 'INVALID' summary."
        ),
        context=[rule_task],
        expected_output="A JSON validation report showing pass/fail for each rule and overall document validity.",
        agent=rule_checker_agent,
        output_file="validation_result.json"
    )   


    # Crew
    crew = Crew(
        agents=[classifier_agent, field_extractor_agent, table_extractor_agent, rule_suggester_agent, rule_checker_agent],
        tasks=[classify_task, field_task, table_task, rule_task, rule_check_task],
        process=Process.sequential,
        verbose=True
    )

    results = crew.kickoff()
    print("results: ", results)
    
    # get data from each file 
    doc_type = read_file("classification_result.txt")
    fields = read_file("fields_result.json")
    tables = read_file("tables_result.json")
    rules = read_file("rules_result.json")
    validation_result = read_file("validation_result.json")

    print(doc_type, fields, tables, rules, validation_result)
    return {
        "type": doc_type,
        "fields": fields,
        "tables": tables,
        "rules": rules,
        "validation_result": validation_result
    }