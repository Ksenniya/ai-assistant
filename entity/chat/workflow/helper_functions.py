import asyncio
import glob
import json
import logging
import os

import aiofiles
import black

from common.config.config import MOCK_AI, VALIDATION_MAX_RETRIES, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO
from common.util.utils import parse_json, get_project_file_name
from entity.chat.data.mock_data_generator import generate_mock_data
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if MOCK_AI== "true":
    #generate_mock_data()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)
    # Build the file path
    mock_external_data_path = os.path.join(current_dir, 'data', "mock_external_data.json")
    try:
        with open(mock_external_data_path, 'r') as file:
            data = file.read()
    except Exception as e:
        logger.error(f"Failed to read JSON file {mock_external_data_path}: {e}")
        raise
    json_mock_data = json.loads(data)


def _sort_entities(entity):
    # Define order of priority
    if entity["entity_type"].endswith("RAW_DATA"):
        return 0
    elif entity["entity_type"].endswith("BUSINESS_ENTITY"):
        return 1
    elif entity["entity_type"].endswith("JOB"):
        return 3
    else:
        return 2


async def _get_valid_result(_data, schema, token, ai_endpoint, chat_id):
    if MOCK_AI=="true" and not isinstance(_data, dict):
        return _data
    result = await ai_service.validate_and_parse_json(token=token,
                                              ai_endpoint=ai_endpoint,
                                              chat_id=chat_id,
                                              data=_data,
                                              schema=schema,
                                              max_retries=VALIDATION_MAX_RETRIES)
    return result


async def run_chat(chat, _event, token, ai_endpoint, chat_id):
    event_prompt, prompt = build_prompt(_event, chat)
    result = await _get_chat_response(prompt=prompt, token=token, ai_endpoint=ai_endpoint, chat_id=chat_id)
    if event_prompt.get("schema"):
        try:
            result = await _get_valid_result(_data=result,
                                     schema=event_prompt["schema"],
                                     token=token,
                                     ai_endpoint=ai_endpoint,
                                     chat_id=chat_id)
        except Exception as e:
            return {"success": "false", "error": str(e)}
    return result


def build_prompt(_event, chat):
    if _event.get("function") and _event["function"].get("prompt"):
        event_prompt = _event["function"]["prompt"]
    else:
        event_prompt = _event.get("prompt", {})
    prompt_text = _enrich_prompt_with_context(_event, chat, event_prompt)
    prompt = f'{prompt_text}: {_event.get("answer", "")}' if _event.get(
        "answer") else prompt_text
    prompt = f'{prompt}. Use this json schema http://json-schema.org/draft-07/schema# to understand how to structure your answer: {event_prompt.get("schema", "")}. It will be validated against this schema. Return only json (python dictionary)' if event_prompt.get(
        "schema") else prompt
    return event_prompt, prompt

def _enrich_prompt_with_context(_event, chat, event_prompt):
    prompt_text = event_prompt.get("text", "")
    prompt_context = _event.get("context", {}).get("prompt", {})
    if prompt_context:
        # Loop through each item in the context dictionary
        for prompt_context_item, prompt_item_values in prompt_context.items():
            chat_context = chat.get('cache', {})
            # Assuming prompt_item_value is a dictionary with keys to resolve in chat_context
            if isinstance(prompt_item_values, list):
                for item in prompt_item_values:
                    chat_context = chat_context.get(item, {})
            # After finding the correct value in chat_context, replace in the prompt_text
            if chat_context:
                prompt_text = prompt_text.replace(f'${prompt_context_item}', str(chat_context))
    return prompt_text


async def _get_chat_response(prompt, token, ai_endpoint, chat_id):
    """Get chat response either from the AI service or mock entity."""
    if MOCK_AI=="true":
        return _mock_ai(prompt)
    resp = await ai_service.ai_chat(token=token, ai_endpoint=ai_endpoint, chat_id=chat_id, ai_question=prompt)
    return resp


def _mock_ai(prompt_text):
    return json_mock_data.get(prompt_text[:15], json.dumps({"entity": "some random text"}))


def get_event_template(question, notification, answer, prompt, event):
    # Predefined keys for the final JSON structure
    final_json = {
        "question": question,  # Sets the provided question
        "prompt": prompt,  # Sets the provided prompt
        "notification": notification,
        "answer": answer,  # Initially no answer
        "function": event.get('prompt', {}).get('function', {}),  # Placeholder for function
        "index": event.get('index', 0),  # Default index
        "iteration": event.get('iteration', 0),  # Initial iteration count
        "max_iteration": event.get('max_iteration', 0),
        "data": event.get('data', {}),
        "entity": event.get('entity', {}),
        "file_name": event.get('file_name', ''),
        "context": event.get('context', {})
    }

    # Iterate through additional key-value pairs in the event object
    for key, value in event.items():
        if key not in final_json:  # Only add key-value pairs not already in final_json
            final_json[key] = value

    return final_json


async def _save_file(chat_id, _data, item) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}")
    file_path = os.path.join(target_dir, item)
    logger.info(f"Saving to {file_path}")

    # Use asyncio.to_thread for non-blocking creation of directories
    await asyncio.to_thread(os.makedirs, os.path.dirname(file_path), exist_ok=True)

    # Process the data and get the output to save
    output_data = _process_data(_data)

    # Write the processed output data to the file asynchronously
    async with aiofiles.open(file_path, 'w') as output:
        await output.write(output_data)

    logger.info(f"saved to {file_path}")

    # Define the path for __init__.py in the target directory
    init_file_target_dir = os.path.dirname(file_path)
    init_file = os.path.join(init_file_target_dir, "__init__.py")
    file_paths_to_commit = [file_path]

    # Check if __init__.py exists asynchronously
    init_file_exists = await asyncio.to_thread(os.path.exists, init_file)

    if not init_file_exists:
        # If __init__.py does not exist, create it (empty __init__.py file)
        async with aiofiles.open(init_file, 'w') as f:
            pass  # Just create an empty __init__.py file

        logger.info(f"Created {init_file}")
        file_paths_to_commit.append(init_file)

    if CLONE_REPO == "true":
        await _git_push(chat_id, file_paths_to_commit, commit_message=f"saved {item}")

    logger.info(f"pushed to git")

    return str(file_path)


def _format_code(code):
    try:
        # Format the code using black's formatting
        formatted_code = black.format_str(code, mode=black.Mode())
        return formatted_code
    except Exception as e:
        print(f"Error formatting code: {e}")
        return code  # Return the original code if formatting fails

def test_format_code():
    # Test code to format
    test_code = """"
def hello_world():
    print('Hello World!')
    for i in range(5):
        print(i)
    """

    # Format the code
    formatted = _format_code(test_code)

    # Print original and formatted code
    print("Original code:")
    print(test_code)
    print("\nFormatted code:")
    print(formatted)


# Function to process the data
def _process_data(_data):
    # Try to parse the string if it's a string
    if isinstance(_data, str):
        try:
            # Try to parse as JSON
            _data = parse_json(_data)
            _data = json.loads(_data)
        except Exception as e:
            # If it's not valid JSON, treat it as plain string
            return comment_out_non_code(_data)

    # If it's a dictionary or list, handle it as JSON
    if isinstance(_data, dict) and 'code' in _data:
        # If 'code' exists, format the code
        return _format_code(_data['code'])

    if not isinstance(_data, dict) and not isinstance(_data, list):
        return comment_out_non_code(_data)

    # Otherwise, return JSON as a formatted string
    return json.dumps(_data, indent=4)




async def _export_workflow_to_cyoda_ai(token, chat_id, _data):
    if MOCK_AI=="true":
        return
    if _data.get("transitions"):
        _data.get("transitions")[0]["start_state"] = "None"

    await ai_service.export_workflow_to_cyoda_ai(token=token, chat_id=chat_id, data = _data)

async def git_pull(chat_id):
    clone_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}"

    try:
        # Start the `git checkout` command asynchronously with the --git-dir and --work-tree options
        checkout_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'checkout', str(chat_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await checkout_process.communicate()

        if checkout_process.returncode != 0:
            logger.error(f"Error during git checkout: {stderr.decode()}")
            return

        # Now, run the `git pull` command asynchronously with the --git-dir and --work-tree options
        pull_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'pull', 'origin', str(chat_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await pull_process.communicate()

        if pull_process.returncode != 0:
            logger.error(f"Error during git pull: {stderr.decode()}")
            return

        logger.info(f"Git pull successful: {stdout.decode()}")

    except Exception as e:
        logger.error(f"Unexpected error during git pull: {e}")
        logger.exception(e)

async def _git_push(chat_id, file_paths: list, commit_message: str):
    await git_pull(chat_id=chat_id)

    clone_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}"

    try:
        # Create a new branch with the name $chat_id
        checkout_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'checkout', str(chat_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await checkout_process.communicate()
        if checkout_process.returncode != 0:
            logger.error(f"Error during git checkout: {stderr.decode()}")
            return

        # Add files to the commit
        for file_path in file_paths:
            add_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'add', file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await add_process.communicate()
            if add_process.returncode != 0:
                logger.error(f"Error during git add {file_path}: {stderr.decode()}")
                return

        # Commit the changes
        commit_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'commit', '-m', f"{commit_message}: {chat_id}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await commit_process.communicate()
        if commit_process.returncode != 0:
            logger.error(f"Error during git commit: {stderr.decode()}")
            return

        # Push the new branch to the remote repository
        push_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'push', '-u', 'origin', str(chat_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await push_process.communicate()
        if push_process.returncode != 0:
            logger.error(f"Error during git push: {stderr.decode()}")
            return

        logger.info("Git push successful!")

    except Exception as e:
        logger.error(f"Unexpected error during git push: {e}")
        logger.exception(e)


async def _send_notification(chat, event, notification_text):
    stack = chat["chat_flow"]["current_flow"]
    notification_event = get_event_template(notification=notification_text,
                                            event = event,
                                            question='',
                                            answer='',
                                            prompt={})
    stack.append(notification_event)
    return stack

async def _send_notification_with_file(chat, event, notification_text, file_name, editable):
    stack = chat["chat_flow"]["current_flow"]
    notification_event = get_event_template(notification=notification_text,
                                            event = event,
                                            question='',
                                            answer='',
                                            prompt={})
    notification_event['file_name']=file_name
    notification_event['editable']=editable
    stack.append(notification_event)
    return stack

async def _build_context_from_project_files(chat, files, excluded_files):
    contents = []
    for file_pattern in files:
        root_path = get_project_file_name(chat["chat_id"], file_pattern)
        if "**" in root_path or os.path.isdir(root_path):
            # Use glob to get all files matching the pattern (including files in subdirectories)
            for file_path in glob.glob(root_path, recursive=True):  # recursive=True to include files in subdirectories
                if os.path.isfile(file_path) and not any(file_path.endswith(excluded) for excluded in excluded_files):
                    async with aiofiles.open(file_path, "r") as f:
                        contents.append({file_path: f.read()})
        else:
            file_path = get_project_file_name(chat["chat_id"], file_pattern)
            # Check if the file exists before trying to open it
            if os.path.isfile(file_path):
                async with aiofiles.open(file_path, "r") as f:
                    contents.append({file_pattern: f.read()})
    return contents


async def main_build_context():
    # Test parameters
    chat = {"chat_id": "8bd9a020-c073-11ef-a0cd-40c2ba0ac9eb"}
    files = ["entity/**"]
    excluded_files = ["entity/workflow.py"]

    # Call function with test parameters
    contents = await _build_context_from_project_files(chat, files, excluded_files)

    # Print results
    print("Files found:")
    for content in contents:
        for file_path, file_content in content.items():
            print(f"\nFile: {file_path}")
            print("Content preview (first 100 chars):")
            print(file_content[:100])


async def save_result_to_file(chat, _event, _data):
    file_name = _event.get("file_name")
    if file_name:
        await _save_file(chat_id=chat["chat_id"], _data=_data, item=file_name)
        notification_text = f"I've pushed the changes to {file_name} . Could you please take a look when you get a chance? 😸"
        await _send_notification(chat=chat, event=_event, notification_text=notification_text)


def comment_out_non_code(text):
    if '```python' in text:
        lines = text.splitlines()
        in_python_block = False
        commented_lines = []

        for line in lines:
            if line.strip().startswith("```python"):
                # Comment out the ```python line
                commented_lines.append(f"# {line}")
                in_python_block = True
            elif line.strip().startswith("```") and in_python_block:
                # Comment out the ``` line
                commented_lines.append(f"# {line}")
                in_python_block = False
            elif in_python_block:
                # Keep lines inside the Python block as-is
                commented_lines.append(line)
            else:
                # Comment out lines outside the Python block
                commented_lines.append(f"# {line}")

        return "\n".join(commented_lines)
    else:
        return text



def main():
    input = """```python
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceClient:
    BASE_URL = 'https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/'

    def get_london_houses(self, params=None):
        url = f"{self.BASE_URL}london_houses.csv"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text

    def get_paris_apartments(self, params=None):
        url = f"{self.BASE_URL}paris_apartments.csv"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text

    def get_new_york_condos(self, params=None):
        url = f"{self.BASE_URL}new_york_condos.csv"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text

def ingest_data(source_type=None):
    client = DataSourceClient()
    if source_type == 'london_houses':
        data = client.get_london_houses()
    elif source_type == 'paris_apartments':
        data = client.get_paris_apartments()
    elif source_type == 'new_york_condos':
        data = client.get_new_york_condos()
    else:
        logger.error("Invalid source type specified.")
        return None
    logger.info("Data ingested successfully.")
    return data

def main():
    source_type = 'london_houses'  # Example input, can be changed for testing
    data = ingest_data(source_type)
    logger.info(data)

if __name__ == "__main__":
    main()
```

Please validate the provided code to ensure it meets your requirements.
"""
    print(comment_out_non_code(input))


if __name__ == "__main__":
    main()