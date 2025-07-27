from llm_client import call_llm
from executor import execute_code
import time
from utils import extract_python_code, format_metadata_list

def scraping_required(task: str) -> bool:
    messages = [
        {"role": "system", "content": "You are a data analysis assistant."},
        {"role": "user", "content": f"Does this task require web scraping? If the data source is unstructured, reply with 'no'.\n\n{task}\n\nReply with just 'yes' or 'no'."}
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
You are a Data analyst expert. Your job is to solve the following data analysis task:

Task:
{task}


Use the metadata(if present) below to scrape or fetch any required data and solve the task.
The meta data provides information about the data sources and the structure of the data. But not all the data structures given in the metadata mey be relevant for the given task. So select the apropriate data structure to solve the task.


Metadata:
{metadata_text}


Important:
Run and store the final output in the variable called result in the format clearly described in the task.

Points to consider: 
-Clean the data wherever possible as it comes from raw source.
-Ignore references and footnotes typically found in <sup> tags.(specially for wikipedia data)
-Use Metadata(if present) as reference to find scope of cleaning a particular column.
-The code should be a single Python code block. No comments , keep it precise and clean.
-Always use matplotlib.use('Agg') before importing matplotlib.pyplot to ensure compatibility in headless servers.
-Add print statements to debug your code.
-Do proper error handling and resilience to bad or missing structures.
-Each question solution should have it's own try and except block with proper error information printed.
-If error occurs while solving a particular question then it should go to the next question without interrupting the process.
"""
    messages = [
        {"role": "system", "content": "You are a data analyst expert."},
        {"role": "user", "content": prompt}
    ]

    return call_llm(messages)


def run_pipeline(task: str):
    metadata_list = []

    if scraping_required(task):
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
    print("\n✅ Final result:\n", result)

    return result