import json
import logging
import os
import subprocess

import requests

from common.config.config import INSTRUCTION_URL, MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL
from entity.chat.data.data import scheduler_stack, api_request_stack, form_submission_stack, \
    file_upload_stack, external_datasource_stack, workflow_stack, entity_stack
from entity.chat.workflow.helper_functions import _save_code_to_file, _save_file, _chat, _save_json_entity_to_file, _export_workflow_to_cyoda_ai
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_chats(token, _event, chat):
    if (MOCK_AI=="true"):
        return
    ai_service.init_chat_cyoda(token=token, chat_id=chat["chat_id"])
    ai_service.init_workflow_chat(token=token, chat_id=chat["chat_id"])


def add_instruction(token, _event, chat):
    response = requests.get(INSTRUCTION_URL)
    if response.status_code == 200:
        instruction_text = response.text
    else:
        instruction_text = None
        print(f"Failed to retrieve file: {response.status_code}")
    if "prompt" not in _event["function"]:
        _event["function"]["prompt"] = {}
    _event["function"]["prompt"]["text"] = instruction_text
    _chat(_event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


def add_design_stack(token, _event, chat) -> list:
    design = _chat(_event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    target_dir = 'entity'
    _save_file(chat_id=chat["chat_id"], data=json.dumps(design), target_dir=target_dir, item=f'app_design.json')
    entry_point_to_stack = {
        "SCHEDULER": scheduler_stack,
        "API_REQUEST": api_request_stack,
        "FORM_SUBMISSION": form_submission_stack,
        "FILE_UPLOAD": file_upload_stack,
        "EXTERNAL_DATA_SOURCE": external_datasource_stack
    }
    reversed_design_entities = design["entities"][::-1]
    stack = chat["chat_flow"]["current_flow"]
    for entity in reversed_design_entities:
        entry_point = entity.get("entity_entry_point")
        if entry_point in entry_point_to_stack:
            stack.extend(entry_point_to_stack[entry_point](entity))
    for entity in reversed_design_entities:
        if entity.get("entity_workflow") and entity.get("entity_workflow").get("transitions"):
            stack.extend(workflow_stack(entity))
    for entity in reversed_design_entities:
        stack.extend(entity_stack(entity))
    return stack


def clone_repo(token, _event, chat):
    """
    Clone the GitHub repository to the target directory.
    If the repository should not be copied, it ensures the target directory exists.
    """
    clone_dir = f"{PROJECT_DIR}/{chat["chat_id"]}/{REPOSITORY_NAME}"

    if CLONE_REPO!="true":
        os.makedirs(clone_dir, exist_ok=True)
        logger.info(f"Target directory '{clone_dir}' is created.")
        return

    subprocess.run(["git", "clone", REPOSITORY_URL, clone_dir], check=True)
    os.chdir(clone_dir)
    subprocess.run(["git", "checkout", "-b", str(chat["chat_id"])], check=True)
    logger.info(f"Repository cloned to {clone_dir}")


def save_entity_to_file(token, _event, chat) -> str:
    """
    Save the entity to a JSON file inside a specific directory.
    """
    return _save_json_entity_to_file(_event=_event,
                                     file_name=f"{_event.get('entity').get('entity_name')}.json",
                                     token=token,
                                     ai_endpoint=CYODA_AI_API,
                                     chat_id=chat["chat_id"],
                                     sub_dir='')


def export_workflow(token, _event, chat) -> str:
    """
    Save the workflow to a JSON file inside a specific directory.
    """
    # todo save to cyoda service
    data = _save_json_entity_to_file(_event=_event,
                                     file_name='workflow.json',
                                     token=token,
                                     ai_endpoint=CYODA_AI_API,
                                     chat_id=chat["chat_id"],
                                     sub_dir='')
    _export_workflow_to_cyoda_ai(token=token, chat_id=chat["chat_id"], data=data)
    return data


def save_processors_code_to_file(token, _event, chat) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    entity_name = _event.get("entity").get("entity_name")
    code = _chat(_event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    return _save_code_to_file(chat_id=chat["chat_id"], entity_name=entity_name, data=code["code"], item='workflow')


def save_logic_code_to_file(token, _event, chat) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    entity_name = _event.get("entity").get("entity_name")
    code = _chat(_event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    return _save_code_to_file(chat_id=chat["chat_id"], entity_name=entity_name, data=code["code"], item='logic')


