import json
import logging
import os
import subprocess

from common.config.config import MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL
from common.util.utils import read_file, get_project_file_name
from entity.chat.data.data import scheduler_stack, api_request_stack, \
    external_datasource_stack, workflow_stack, entity_stack, processors_stack
from entity.chat.workflow.helper_functions import _save_file, _chat, _sort_entities, _send_notification, \
    _build_context_from_project_files
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_chats(token, _event, chat):
    if (MOCK_AI == "true"):
        return
    ai_service.init_chat(token=token, chat_id=chat["chat_id"])


def add_instruction(token, _event, chat):
    file_name = _event["file_name"]
    instruction_text = read_file(get_project_file_name(chat["chat_id"], file_name))
    _event.setdefault('function', {}).setdefault("prompt", {}).setdefault("text", instruction_text)
    _chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


def refresh_context(token, _event, chat):
    # clean chat history and re-initialize
    ai_service.init_chat(token=token, chat_id=chat["chat_id"])
    contents = _build_context_from_project_files(chat=chat, files=_event["context"]["files"],
                                                 excluded_files=_event["context"].get("excluded_files"))
    _event.setdefault('function', {}).setdefault("prompt", {})
    _event["function"]["prompt"]["text"] = f"Please remember these files contents and reuse later: {json.dumps(contents)} . Do not do any mapping logic - it is not relevant. Just remember the code and the application design to reuse in your future application building. Return confirmation that you remembered everything"
    _chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


def add_design_stack(token, _event, chat) -> list:
    file_name = _event["file_name"]
    design = json.loads(read_file(get_project_file_name(chat["chat_id"], file_name)))
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

    if CLONE_REPO != "true":
        os.makedirs(clone_dir, exist_ok=True)
        logger.info(f"Target directory '{clone_dir}' is created.")
        return

    subprocess.run(["git", "clone", REPOSITORY_URL, clone_dir], check=True)
    os.chdir(clone_dir)
    subprocess.run(["git", "checkout", "-b", str(chat["chat_id"])], check=True)
    logger.info(f"Repository cloned to {clone_dir}")
    _save_file(chat["chat_id"], chat["chat_id"], 'README.txt')
    notification_text = f"Your project is ready at branch {chat["chat_id"]} in {clone_dir}"
    _send_notification(chat=chat, event=_event, notification_text=notification_text)


def save_raw_data_to_entity_file(token, _event, chat) -> str:
    """
    Save the entity to a JSON file inside a specific directory.
    """
    file_name = _event["file_name"]
    _save_file(chat_id=chat["chat_id"], data=json.dumps(_event["answer"]), item=file_name)
    notification_text = f"Pushing changes for {file_name}"
    _send_notification(chat=chat, event=_event, notification_text=notification_text)
    return _event["answer"]
