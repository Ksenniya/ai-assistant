import json
import logging
import os
import subprocess

import requests

from common.config.config import INSTRUCTION_URL, MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL
from entity.chat.data.data import scheduler_stack, api_request_stack, \
     external_datasource_stack, workflow_stack, entity_stack, processors_stack
from entity.chat.workflow.helper_functions import _save_code_to_file, _save_file, _chat, _save_json_entity_to_file, \
    _export_workflow_to_cyoda_ai, _sort_entities, _get_event_template, _send_notification
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_chats(token, _event, chat):
    if (MOCK_AI=="true"):
        return
    ai_service.init_chat(token=token, chat_id=chat["chat_id"])


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
    _chat(chat = chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])

def save_design_stack(token, _event, chat):
    design = _event["data"]
    target_dir = 'entity'
    file_name = f'app_design.json'
    _save_file(chat_id=chat["chat_id"], data=json.dumps(design), target_dir=target_dir, item=file_name)
    notification_text = f"Pushing changes for {target_dir}/{file_name}"
    _send_notification(chat, notification_text)


def add_design_stack(token, _event, chat) -> list:
    design = _chat(chat = chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    target_dir = 'entity'
    file_name = f'app_design.json'
    _save_file(chat_id=chat["chat_id"], data=json.dumps(design), target_dir=target_dir, item=file_name)
    notification_text = f"Pushing changes for {target_dir}/{file_name}"
    _send_notification(chat, notification_text)
    entry_point_to_stack = {
        "SCHEDULED": scheduler_stack,
        "API_REQUEST": api_request_stack,
    }
    sorted_entities = sorted(design["entities"], key=_sort_entities)
    reversed_design_entities = sorted_entities[::-1]
    stack = chat["chat_flow"]["current_flow"]
    for entity in reversed_design_entities:
        entry_point = entity.get("entity_source")
        if entry_point in entry_point_to_stack:
            stack.extend(entry_point_to_stack[entry_point](entity))
    for entity in reversed_design_entities:
        if entity.get("entity_workflow") and entity.get("entity_workflow").get("transitions"):
            stack.extend(processors_stack(entity))
            stack.extend(workflow_stack(entity))
    for entity in reversed_design_entities:
        if entity["entity_type"] == "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA":
            stack.extend(external_datasource_stack(entity))
        else:
            stack.extend(entity_stack(entity))
    ##know your data
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
    _save_file(chat["chat_id"], chat["chat_id"], '', 'README.txt')
    notification_text = f"Your project is ready at branch {chat["chat_id"]} in {clone_dir}"
    _send_notification(chat, notification_text)


def save_entity_to_file(token, _event, chat) -> str:
    """
    Save the entity to a JSON file inside a specific directory.
    """
    file_name = f"{_event.get('entity').get('entity_name')}.json"
    data = _save_json_entity_to_file(chat = chat,
                                     _event=_event,
                                     file_name=f"{_event.get('entity').get('entity_name')}.json",
                                     token=token,
                                     ai_endpoint=CYODA_AI_API,
                                     chat_id=chat["chat_id"],
                                     sub_dir='')
    chat.setdefault('cache', {}).setdefault(_event.get('entity').get('entity_name'), {})
    chat['cache'][_event.get('entity').get('entity_name')]["data"] = data
    notification_text = f"Pushing changes for {file_name}"
    _send_notification(chat, notification_text)
    return data

def save_raw_data_to_entity_file(token, _event, chat) -> str:
    """
    Save the entity to a JSON file inside a specific directory.
    """
    entity_name = _event.get("entity").get("entity_name")
    target_dir = os.path.join('entity', entity_name, '')
    file_name = f"{_event.get('entity').get('entity_name')}.json"
    _save_file(chat_id=chat["chat_id"], data=json.dumps(_event["answer"]), target_dir=target_dir, item=file_name)
    notification_text = f"Pushing changes for {file_name}"
    _send_notification(chat, notification_text)
    return _event["answer"]

def export_workflow(token, _event, chat) -> str:
    """
    Save the workflow to a JSON file inside a specific directory.
    """
    # todo save to cyoda service
    file_name = 'workflow.json'
    data = _save_json_entity_to_file(chat = chat,
                                     _event=_event,
                                     file_name='workflow.json',
                                     token=token,
                                     ai_endpoint=CYODA_AI_API,
                                     chat_id=chat["chat_id"],
                                     sub_dir='')
    _export_workflow_to_cyoda_ai(token=token, chat_id=chat["chat_id"], data=data)
    notification_text = f"Pushing changes for {file_name}"
    _send_notification(chat, notification_text)
    return data


def save_processors_code_to_file(token, _event, chat) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    entity_name = _event.get("entity").get("entity_name")
    code = _event["data"]
    if isinstance(code, str):
        code = json.loads(code)
    file_name = 'workflow'
    result = _save_code_to_file(chat_id=chat["chat_id"], entity_name=entity_name, data=code.get("code", ""), item=file_name)
    notification_text = f"Pushing changes for {file_name}.py"
    _send_notification(chat, notification_text)
    return result

def save_logic_code_to_file(token, _event, chat) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    entity_name = _event.get("entity").get("entity_name")
    code = _event["data"]
    file_name = 'logic'
    chat.setdefault('cache', {}).setdefault('code', [])
    chat['cache']["code"].append({"logic": code["code"]})
    result = _save_code_to_file(chat_id=chat["chat_id"], entity_name=entity_name, data=code["code"], item=file_name)
    notification_text = f"Pushing changes for {file_name}.py"
    _send_notification(chat, notification_text)
    return result

def save_connections_code_to_file(token, _event, chat) -> str:
    """
    Save the workflow to a file inside a specific directory.
    """
    code = _event["data"]
    #transfer context
    if MOCK_AI!="true":
        ai_service.chat_cyoda(token=token, chat_id=chat["chat_id"], ai_question=f"Please remember this code for ingesting data, they provided public function ingest_data you can use in the next iterations. Please remember it. No answer required. Code: {code}")
    entity_name = _event.get("entity").get("entity_name")
    chat.setdefault('cache', {}).setdefault('code', [])
    chat['cache']["code"].append({"ingest_data": code["code"]})
    file_name = 'connections'
    result = _save_code_to_file(chat_id=chat["chat_id"], entity_name=entity_name, data=code["code"], item=file_name)
    notification_text = f"Pushing changes for {file_name}.py"
    _send_notification(chat, notification_text)
    return result