from llm_client import call_llm
from executor import execute_code
import time
from utils import extract_python_code, format_metadata_list

def scraping_required(task: str) -> bool:
    instructions = ""
    with open("prompts/scraping_required.txt", "r") as f:
        instructions = f.read()
    messages = [
        {
            "role": "system",
            "content": instructions
        },
        {"role": "user", "content": task}
    ]
    response = call_llm(messages)
    print("\nScraping Required:", response)
    return "yes" in response.lower()




def generate_metadata_extraction_code(task: str) -> str:
    instructions = ""
    with open("prompts/extract_metadata.txt", "r") as f:
        instructions = f.read()
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": f"The data-analysis task is:\n{task}"}
    ]
    return call_llm(messages)




def generate_dataframe_code(task: str, metadata: str = None) -> str:
    user_prompt = f"""
    Task:\n{task}\n
    {'Metadata:\n' + metadata if metadata else ''}
    
    Generate Python code to fetch the required data into a pandas DataFrame.
    """
    messages = [
        {"role": "system", "content": "You are a Python data engineer."},
        {"role": "user", "content": user_prompt}
    ]
    return call_llm(messages)




def generate_solution_code(task: str, metadata_list: list) -> str:
    """
    Use the task + optional metadata list to prompt the LLM to generate final solving code
    """
    metadata_text = format_metadata_list(metadata_list) if metadata_list else "No metadata required."

    prompt = f"""
You are a data analysis expert. Generate Python code to solve the following data analysis task.

## Task:
{task}

## Metadata:
{metadata_text}

(Metadata describes potential data sources and structures. Use only the relevant parts.)

---

## Instructions:

- The final code **must be executable immediately**, without requiring the user to call any function manually.
- The code must define and populate two variables by the end:
    - `result` - containing the final output as specified by the task.
    - `error_list` - a list that collects all error messages or exceptions encountered during execution.
- If a function is defined, ensure it is also **called** within the same script.
- Each question or part of the solution must be inside a separate `try/except` block.
    - On exception, append a message to `error_list` and continue.
- Clean the data before use.
    - Specifically, strip or ignore `<sup>` tags (such as footnotes/references in Wikipedia).
- If matplotlib is needed, always begin with:
    ```python
    import matplotlib
    matplotlib.use('Agg')
    ```

---

## Output Format:

- Provide **only** a single clean Python code block — no markdown formatting or extra text.
- Do not include explanations or comments — just the code.
- Ensure the code is minimal, correct, and ready to `exec()`.

"""

    messages = [
        {"role": "system", "content": "You are a data analysis expert."},
        {"role": "user", "content": prompt}
    ]

    return call_llm(messages)



def run_pipeline(task: str):
    metadata_list = []

    if (scraping_required(task)):
        print("\n✅ Scraping is required\n")
        time.sleep(2)

        # Step 1: Generate and execute metadata code
        metadata_code = extract_python_code(generate_metadata_extraction_code(task), True)
        print("\n--- Metadata Code ---\n", metadata_code)

        meta_env = execute_code(metadata_code)
        metadata_list = meta_env.get("metadata_list", [])
        print("\n--- Extracted Metadata ---\n")
        print(metadata_list)

    else:
        print("\n✅ Scraping is NOT required — proceeding directly to solution\n")

    # Step 2: Ask LLM to generate the final code using task + metadata (if any)
    final_code = extract_python_code(generate_solution_code(task, metadata_list), True)
    print("\n--- Final Generated Code ---\n", final_code)

    # Step 3: Execute final solution code
    final_env = execute_code(final_code)
    result = final_env.get("result")
    error_list = final_env.get("error_list")
    if(error_list and len(error_list) > 0):
        print("\n❌ Error List:\n", error_list)

    print("\n✅ Final result:\n", result)

    return result