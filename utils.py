import re
from llm_client import call_llm
import json
import os
import uuid
from datetime import datetime
from pprint import pformat


def load_question(path="question.txt") -> str:
    with open(path, "r") as f:
        return f.read().strip()


def extract_python_code_old(llm_output: str) -> str:
    """
    Extracts the first ```python ... ``` code block from LLM output.
    """
    match = re.search(r"```python\s+([\s\S]+?)\s+```", llm_output)
    if match:
        return match.group(1).strip()
    raise ValueError("No Python code block found in LLM output.")


def extract_python_code(llm_output: str, validate: bool = False) -> str:
    """
    Extracts the first ```python ... ``` code block from LLM output.
    If `validate` is True, sends the extracted code to another LLM for validation and fixes.
    """
    match = re.search(r"```python\s+([\s\S]+?)\s+```", llm_output)
    if not match:
        raise ValueError("No Python code block found in LLM output.")

    code = match.group(1).strip()

    if validate:
        instructions = ""
        with open("prompts/validate_code.txt", "r") as f:
            instructions = f.read()
        messages = [
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": 
                    "Fix any syntax errors, missing imports, runtime bugs, or issues like invalid syntax, missing colons or brackets, and undefined variables "
                    "in the following code. Do NOT change the logic or remove any part of the code:\n\n"
                    "```python\n"
                    f"{code}\n"
                    "```"
            }
        ]
        print("Code before validation ##########################")
        print(code)
        validated_output = call_llm(messages)

        corrected_match = re.search(r"```python\s+([\s\S]+?)\s+```", validated_output)
        if corrected_match:
            return corrected_match.group(1).strip()
        else:
            return validated_output.strip()

    return code


def format_metadata_list(metadata_list: list) -> str:
    """
    Format a list of metadata dictionaries into a readable string for prompting the LLM.

    Each metadata entry should have:
      - 'url': source URL
      - 'metadata': extracted metadata text
    """
    if not metadata_list:
        return "No metadata available."

    result = ""
    for i, item in enumerate(metadata_list, 1):
        result += f"Source {i}:\n"
        result += f"URL: {item.get('url', 'N/A')}\n"
        result += f"Metadata:\n{item.get('metadata', '')}\n\n"
    return result.strip()


def fix_code_with_llm(code: str, errors: list[str]) -> str:
    """
    Ask the LLM to fix the code based on the provided error messages.
    """
    messages = [
        {"role": "system", "content": "You are an expert Python code fixer. Your job is to correct any errors in the given Python code based on the errors shown below. Do not remove or alter correct logic unnecessarily. Fix only what is needed to resolve the errors. Return only the corrected code inside a Python code block."},
        {"role": "user", "content": f"Here is the code:\n\n```python\n{code}\n```\n\nHere are the errors:\n{json.dumps(errors, indent=2)}\n\nReturn the fixed full code:"}
    ]
    return extract_python_code(call_llm(messages))



def setup_logger():
    log_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{log_id}.log")

    def log(msg):
        if isinstance(msg, str):
            formatted = msg
        else:
            formatted = pformat(msg)

        print(formatted)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")

    return log, log_path


def summarize_attachments_for_llm(attachments):
    """
    Returns a string that includes both metadata and real paths so the LLM
    can load these files in generated code.
    """
    if not attachments:
        return "No additional files provided."

    lines = ["Available files for use in your Python code:"]
    for i, att in enumerate(attachments, start=1):
        size = len(att["content_bytes"])
        mime = att["content_type"]
        path = att["tmp_path"] or "(not saved)"
        lines.append(f"{i}. {att['filename']} — {mime} — {size} bytes — saved at {path}")
    return "\n".join(lines)

