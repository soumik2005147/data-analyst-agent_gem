import re
from llm_client import call_llm

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
