import json
import logging
import os
import shutil
import subprocess

from common.config.config import MOCK_AI, VALIDATION_MAX_RETRIES, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO
from common.util.utils import read_file
from entity.app_builder_job.data.mock_data_generator import generate_mock_data
from logic.init import ai_service, chat_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if (MOCK_AI=="true"):
    generate_mock_data()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)
    # Build the file path
    mock_external_data_path = os.path.join(current_dir, 'data', "mock_external_data.json")
    data = read_file(mock_external_data_path)
    json_mock_data = json.loads(data)


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


def _chat(_event, token, ai_endpoint, chat_id):
    if _event.get("function") and _event["function"].get("prompt"):
        event_prompt = _event["function"]["prompt"]
    else:
        event_prompt = _event.get("prompt", {})

    prompt = f'{event_prompt.get("text", "")}: {_event.get("answer", "")}' if _event.get("answer") else event_prompt.get(
        "text", "")
    prompt = f'{prompt}. Use this json schema http://json-schema.org/draft-07/schema# to understand how to structure your answer: {event_prompt.get("schema", "")}. It will be validated against this schema. Return only json (python dictionary)' if event_prompt.get("schema") else prompt
    result = _get_chat_response(prompt=prompt, token=token, ai_endpoint=ai_endpoint, chat_id=chat_id)
    if event_prompt.get("schema"):
        return _get_valid_result(data=result,
                                 schema=event_prompt["schema"],
                                 token=token,
                                 ai_endpoint=ai_endpoint,
                                 chat_id=chat_id)

    return result



def _get_chat_response(prompt, token, ai_endpoint, chat_id):
    """Get chat response either from the AI service or mock entity."""
    if MOCK_AI=="true":
        return _mock_ai(prompt)

    return ai_service.ai_chat(token=token, ai_endpoint=ai_endpoint, chat_id=chat_id, ai_question=prompt)


def _mock_ai(prompt_text):
    return json_mock_data.get(prompt_text[:15], json.dumps({"entity": "some random text"}))


def _get_event_template(question: str, prompt: str, max_iteration: int = 0):
    return {
        "question": question,  # Sets the provided question
        "prompt": prompt,  # Sets the provided prompt
        "answer": "",  # Initially no answer
        "function": None,  # Placeholder for function
        "index": 0,  # Default index
        "iteration": 0,  # Initial iteration count
        "max_iteration": max_iteration  # Sets the maximum iteration
    }


def _save_code_to_file(entity_name, data, item):
    target_dir = os.path.join('entity', entity_name, item)
    return _save_file(data=data, target_dir=target_dir, item=f'{item}.py')


def _save_json_entity_to_file(_event, sub_dir: str, file_name: str, token, ai_endpoint, chat_id) -> str:
    """
    A helper function to handle the extraction, parsing, and saving of a JSON entity.
    """
    entity_name = _event.get("entity").get("entity_name")
    data = _chat(_event=_event,
                 token=token,
                 ai_endpoint=ai_endpoint,
                 chat_id=chat_id)

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("The provided entity is a string but is not valid JSON.")

    target_dir = os.path.join('entity', entity_name, sub_dir)
    _save_file(json.dumps(data), target_dir, file_name)
    return data


def _save_file(data, target_dir, item) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}", target_dir)
    logger.info(f"Saving to {target_dir}")
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, item)
    logger.info(f"Saving to {file_path}")
    with open(file_path, 'w') as output:
        output.write(data)
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

    for file_path in file_paths:
        subprocess.run(["git", "add", file_path], check=True)

    # Commit the changes
    subprocess.run(["git", "commit", "-m", f"{commit_message}: {chat_id}"], check=True)

    # Push the new branch to the remote repository
    subprocess.run(["git", "push", "-u", "origin", str(chat_id)], check=True)
