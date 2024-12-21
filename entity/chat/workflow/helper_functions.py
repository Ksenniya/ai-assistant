import glob
import json
import logging
import os
import shutil
import subprocess
import time

from common.config.config import MOCK_AI, VALIDATION_MAX_RETRIES, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO
from common.util.utils import read_file, get_project_file_name
from entity.chat.data.mock_data_generator import generate_mock_data
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if MOCK_AI== "true":
    generate_mock_data()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)
    # Build the file path
    mock_external_data_path = os.path.join(current_dir, 'data', "mock_external_data.json")
    data = read_file(mock_external_data_path)
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



def _copy_template_project(source_dir, target_dir):
    """
    Copies the template project from the source directory to the target directory.
    Handles potential errors during the copy operation.
    """
    try:
        shutil.copytree(source_dir, target_dir)
        logger.info(f"Copied template project to {target_dir}.")
    except OSError as e:
        logger.error(f"Error copying template project: {e}")


def _get_valid_result(data, schema, token, ai_endpoint, chat_id):
    if MOCK_AI=="true" and not isinstance(data, dict):
        return data
    return ai_service.validate_and_parse_json(token=token,
                                              ai_endpoint=ai_endpoint,
                                              chat_id=chat_id,
                                              data=data,
                                              schema=schema,
                                              max_retries=VALIDATION_MAX_RETRIES)


def _chat(chat, _event, token, ai_endpoint, chat_id):
    event_prompt, prompt = build_prompt(_event, chat)
    result = _get_chat_response(prompt=prompt, token=token, ai_endpoint=ai_endpoint, chat_id=chat_id)
    if event_prompt.get("schema"):
        return _get_valid_result(data=result,
                                 schema=event_prompt["schema"],
                                 token=token,
                                 ai_endpoint=ai_endpoint,
                                 chat_id=chat_id)

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


def _get_chat_response(prompt, token, ai_endpoint, chat_id):
    """Get chat response either from the AI service or mock entity."""
    if MOCK_AI=="true":
        return _mock_ai(prompt)

    return ai_service.ai_chat(token=token, ai_endpoint=ai_endpoint, chat_id=chat_id, ai_question=prompt)


def _mock_ai(prompt_text):
    return json_mock_data.get(prompt_text[:15], json.dumps({"entity": "some random text"}))


def _get_event_template(question: str, prompt: str,  notification: str, function: str, result_data: str, entity, max_iteration: int = 0):
    return {
        "question": question,  # Sets the provided question
        "prompt": prompt,  # Sets the provided prompt
        "notification": notification,
        "answer": "",  # Initially no answer
        "function": function,  # Placeholder for function
        "index": 0,  # Default index
        "iteration": 0,  # Initial iteration count
        "max_iteration": max_iteration,
        "data": result_data,
        "entity": entity,
    }


def _save_code_to_file(chat_id, data, item):
    return _save_file(chat_id=chat_id, data=data, item=f'{item}.py')


def _save_json_entity_to_file(chat, _event, sub_dir: str, file_name: str, token, ai_endpoint, chat_id) -> str:
    """
    A helper function to handle the extraction, parsing, and saving of a JSON entity.
    """
    entity_name = _event.get("entity").get("entity_name")
    data = _event["data"]

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("The provided entity is a string but is not valid JSON.")
    _save_file(chat_id=chat_id, data=json.dumps(data), item=file_name)
    return data


def _save_file(chat_id, data, item) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}")
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, item)
    logger.info(f"Saving to {file_path}")
    with open(file_path, 'w') as output:
        output.write(str(data))
    logger.info(f"saved to {file_path}")
    if CLONE_REPO=="true":
        _git_push(chat_id,  [file_path], commit_message=f"saved {item}")
    logger.info(f"pushed to git")

    return str(file_path)


def _export_workflow_to_cyoda_ai(token, chat_id, data):
    if MOCK_AI=="true":
        return
    if data.get("transitions"):
        data.get("transitions")[0]["start_state"] = "None"

    ai_service.export_workflow_to_cyoda_ai(token=token, chat_id=chat_id, data = data)


def _git_push(chat_id, file_paths: list, commit_message: str):

    clone_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}"
    os.chdir(clone_dir)
    # Create a new branch with the name $chat_id
    subprocess.run(["git", "checkout", str(chat_id)], check=True)
    try:
        for file_path in file_paths:
            subprocess.run(["git", "add", file_path], check=True)
        # Commit the changes
        subprocess.run(["git", "commit", "-m", f"{commit_message}: {chat_id}"], check=True)
        # Push the new branch to the remote repository
        subprocess.run(["git", "push", "-u", "origin", str(chat_id)], check=True)
    except Exception as e:
        logger.error(f"Error during git push: {e}")
        logger.exception(e)

def _send_notification(chat, notification_text):
    stack = chat["chat_flow"]["current_flow"]
    notification_event = _get_event_template(notification=notification_text, prompt='', max_iteration=0, question='',
                                             result_data='', function='', entity=None)
    stack.append(notification_event)
    return stack


def _build_context_from_project_files(chat, files):
    contents = []
    for file_pattern in files:
        root_path = get_project_file_name(chat["chat_id"], file_pattern)
        if "*" in root_path or os.path.isdir(root_path):  # Check if it's a wildcard or directory
            # Use glob to get all files matching the pattern (including files in subdirectories)
            for file_path in glob.glob(root_path):
                if os.path.isfile(file_path):  # Ensure it's a file
                    with open(file_path, "r") as f:
                        contents.append({file_path: f.read()})
        else:  # Handle exact paths
            with open(get_project_file_name(chat["chat_id"], file_pattern), "r") as f:
                contents.append({file_pattern: f.read()})
    return contents

