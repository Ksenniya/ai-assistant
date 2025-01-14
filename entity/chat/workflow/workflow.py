import json
import asyncio
import os
import logging

from common.config.config import MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL, WORKFLOW_AI_API
from common.config.conts import SCHEDULED_STACK, API_REQUEST_STACK, \
    WORKFLOW_STACK, \
    ENTITY_STACK, PROCESSORS_STACK, EXTERNAL_SOURCES_PULL_BASED_RAW_DATA, WEB_SCRAPING_PULL_BASED_RAW_DATA, \
    TRANSACTIONAL_PULL_BASED_RAW_DATA
from common.util.utils import read_file, get_project_file_name, parse_json, parse_workflow_json
from entity.chat.data.data import scheduler_stack, api_request_stack, workflow_stack, entity_stack, processors_stack, \
    data_ingestion_stack
from entity.chat.workflow.helper_functions import _save_file, _sort_entities, _send_notification, \
    _build_context_from_project_files, run_chat, _send_notification_with_file
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entry_point_to_stack = {
        SCHEDULED_STACK: scheduler_stack,
        API_REQUEST_STACK: api_request_stack,
        EXTERNAL_SOURCES_PULL_BASED_RAW_DATA: data_ingestion_stack,
        WEB_SCRAPING_PULL_BASED_RAW_DATA: data_ingestion_stack,
        TRANSACTIONAL_PULL_BASED_RAW_DATA: data_ingestion_stack,
        WORKFLOW_STACK: workflow_stack,
        ENTITY_STACK: entity_stack,
        PROCESSORS_STACK: processors_stack
    }

async def init_chats(token, _event, chat):
    if MOCK_AI == "true":
        return
    await ai_service.init_chat(token=token, chat_id=chat["chat_id"])


async def add_instruction(token, _event, chat):
    file_name = _event["file_name"]
    instruction_text = await read_file(get_project_file_name(chat["chat_id"], file_name))
    _event.setdefault('function', {}).setdefault("prompt", {}).setdefault("text", instruction_text)
    await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


async def refresh_context(token, _event, chat):
    # clean chat history and re-initialize
    await ai_service.init_cyoda_chat(token=token, chat_id=chat["chat_id"])
    contents = await _build_context_from_project_files(chat=chat, files=_event["context"]["files"],
                                                       excluded_files=_event["context"].get("excluded_files"))
    _event.setdefault('function', {}).setdefault("prompt", {})
    _event["function"]["prompt"][
        "text"] = f"Please remember these files contents and reuse later: {json.dumps(contents)} . Do not do any mapping logic - it is not relevant. Just remember the code and the application design to reuse in your future application building. Return confirmation that you remembered everything"
    await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


async def add_design_stack(token, _event, chat) -> list:
    file_name = _event["file_name"]
    file = await read_file(get_project_file_name(chat["chat_id"], file_name))
    design = json.loads(file)
    sorted_entities = sorted(design["entities"], key=_sort_entities)
    reversed_design_entities = sorted_entities[::-1]
    stack = chat["chat_flow"]["current_flow"]
    entities_dict = {ENTITY_STACK: []}
    # Process entities by entity_source or workflow transitions
    for entity in reversed_design_entities:
        entity_source = entity.get("entity_source")
        entity_workflow = entity.get("entity_workflow")
        # Add entities to stack based on entity_source
        if entity_source in entry_point_to_stack:
            stack.extend(entry_point_to_stack[entity_source](entity))
        # Add entities with transitions to stack based on workflow
        if entity_workflow and entity_workflow.get("transitions"):
            stack.extend(entry_point_to_stack[PROCESSORS_STACK](entity))
            stack.extend(entry_point_to_stack[WORKFLOW_STACK](entity))
        # Organize entities by entity_type into entities_dict
        entity_type = entity.get("entity_type")
        if entity_type in entry_point_to_stack:
            if entity_type not in entities_dict:
                entities_dict[entity_type] = []
            entities_dict[entity_type].append(entity)
        else:
            entities_dict[ENTITY_STACK].append(entity)
    for stack_key in [##ENTITY_STACK##,
         WEB_SCRAPING_PULL_BASED_RAW_DATA,
                      TRANSACTIONAL_PULL_BASED_RAW_DATA, EXTERNAL_SOURCES_PULL_BASED_RAW_DATA]:
        if stack_key in entities_dict:
            stack.extend(entry_point_to_stack.get(stack_key, lambda x: [])(entities_dict[stack_key]))

    ##know your data
    return stack


async def add_user_requirement(token, _event, chat):
    file_name = _event["file_name"]
    ai_question = f"Please write a detailed summary of the user requirement. Include all the necessary details specified by the user."
    user_requirement = await ai_service.ai_chat(token=token, chat_id=chat["chat_id"], ai_endpoint=CYODA_AI_API,
                                                ai_question=ai_question)
    await _save_file(chat_id=chat["chat_id"], _data=user_requirement, item=file_name)


async def clone_repo(token, _event, chat):
    """
    Clone the GitHub repository to the target directory.
    If the repository should not be copied, it ensures the target directory exists.
    """
    clone_dir = f"{PROJECT_DIR}/{chat['chat_id']}/{REPOSITORY_NAME}"

    if CLONE_REPO != "true":
        # Create the directory asynchronously using asyncio.to_thread
        await asyncio.to_thread(os.makedirs, clone_dir, exist_ok=True)
        logger.info(f"Target directory '{clone_dir}' is created.")
        return

    # Asynchronously clone the repository using subprocess
    clone_process = await asyncio.create_subprocess_exec(
        'git', 'clone', REPOSITORY_URL, clone_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await clone_process.communicate()

    if clone_process.returncode != 0:
        logger.error(f"Error during git clone: {stderr.decode()}")
        return

    # Asynchronously checkout the branch using subprocess
    checkout_process = await asyncio.create_subprocess_exec(
        'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
        'checkout', '-b', str(chat["chat_id"]),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await checkout_process.communicate()

    if checkout_process.returncode != 0:
        logger.error(f"Error during git checkout: {stderr.decode()}")
        return

    logger.info(f"Repository cloned to {clone_dir}")

    # Call the async _save_file function
    await _save_file(chat['chat_id'], chat['chat_id'], 'README.txt')

    # Prepare the notification text
    notification_text = f"🎉 Your branch is ready! Please update the project and check it out when you get a chance. 😊: {chat['chat_id']}"

    # Call the async _send_notification function
    await _send_notification(chat=chat, event=_event, notification_text=notification_text)


async def save_raw_data_to_entity_file(token, _event, chat) -> str:
    """
    Save the entity to a JSON file inside a specific directory.
    """
    file_name = _event["file_name"]
    await _save_file(chat_id=chat["chat_id"], _data=json.dumps(_event["answer"]), item=file_name)
    notification_text = f"I've pushed the changes to {file_name} . Could you please take a look when you get a chance? 😸"
    await _send_notification(chat=chat, event=_event, notification_text=notification_text)
    return _event["answer"]


async def generate_cyoda_workflow(token, _event, chat):
    # sourcery skip: use-named-expression
    if MOCK_AI == "true":
        return
    try:
        if (_event.get("entity").get("entity_workflow") and _event.get("entity").get("entity_workflow").get(
                "transitions")):
            ai_question = f"what workflow could you recommend for this sketch: {json.dumps(_event.get("entity").get("entity_workflow"))}. All transitions automated, no criteria needed, only externalized processors allowed, calculation node = {chat["chat_id"]}  , calculation_response_timeout_ms = 120000 .  Return only json without any comments."
            resp = await ai_service.ai_chat(token=token, chat_id=chat["chat_id"], ai_endpoint=WORKFLOW_AI_API,
                                            ai_question=ai_question)
            workflow = parse_workflow_json(resp)
            workflow_json = json.loads(workflow)
            workflow_json["workflow_criteria"] = {
                "externalized_criteria": [

                ],
                "condition_criteria": [
                    {
                        "name": _event.get("entity").get("entity_name"),
                        "description": "Workflow criteria",
                        "condition": {
                            "group_condition_operator": "AND",
                            "conditions": [
                                {
                                    "field_name": "entityModelName",
                                    "is_meta_field": True,
                                    "operation": "equals",
                                    "value": _event.get("entity").get("entity_name"),
                                    "value_type": "strings"
                                }
                            ]
                        }
                    }
                ]
            }
            await _save_file(chat_id=chat["chat_id"], _data=json.dumps(workflow_json), item=_event["file_name"])
    except Exception as e:
        logger.error(f"Error generating workflow: {e}")
        logger.exception("Error generating workflow")


async def generate_data_ingestion_entities_template(token, _event, chat):
    entities = _event.get("entities", [])
    files_notifications = _event.get("files_notifications", {})
    if not entities:
        logger.warning("No entities found in the event.")
    for entity in entities:
        try:
            entity_name = entity.get("entity_name")
            for resource_type, notification_info in files_notifications.items():
                file_name_template = notification_info.get("file_name", "")
                file_text_template = notification_info.get("text", "")
                file_name = file_name_template.format(entity_name=entity_name)
                file_text = file_text_template.format(entity_name=entity_name)
                if file_name and file_text:
                    await _save_file(chat_id=chat["chat_id"], _data=json.dumps(file_text), item=file_name)
                    await _send_notification_with_file(chat=chat, event=_event, notification_text=f"file_name: {file_name} \n {file_text}",
                                                       file_name=file_name, editable=True)
        except Exception as e:
            logger.error(f"Unexpected error for entity {entity.get("entity_name")}: {e}")
            logger.exception(e)


async def check_entity_definitions(token, _event, chat):
    entities = _event.get("entities", [])
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat["chat_id"]}/{REPOSITORY_NAME}")
    files_notifications = _event.get("files_notifications", {})
    if not entities:
        logger.warning("No entities found in the event.")
    for entity in entities:
        try:
            entity_name = entity.get("entity_name")
            for resource_type, notification_info in files_notifications.items():
                file_name_template = notification_info.get("file_name", "")
                file_text_template = notification_info.get("text", "")
                file_name = file_name_template.format(entity_name=entity_name)
                file_text = file_text_template.format(entity_name=entity_name)
                if file_name and file_text:
                    file_path = os.path.join(target_dir, file_name)
                    current_file_text = await read_file(file_path)
                    if current_file_text == file_text:
                        notification_text = _event.get("notification_text").format(file_name=file_name)
                        await _send_notification_with_file(chat=chat, event=_event, notification_text=notification_text,
                                                           file_name=file_name, editable=True)
        except Exception as e:
            logger.error(f"Unexpected error for entity {entity.get("entity_name")}: {e}")
            logger.exception(e)


async def generate_data_ingestion_code(token, _event, chat):
    entities = _event.get("entities")
    #
    # for each entity ask question get event
    # . get prompt by entity type
    # save answer to file
    # entity/entity_name/connections/connections.py
    # send notification
    entities = _event.get("entities", [])
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat["chat_id"]}/{REPOSITORY_NAME}")
    files_notifications = _event.get("files_notifications", {})
    if not entities:
        logger.warning("No entities found in the event.")
    for entity in entities:
        try:
            entity_name = entity.get("entity_name")
            code_info = files_notifications.get("code")
            doc_info = files_notifications.get("doc")
            entity_info = files_notifications.get("entity")
            raw_data_info = files_notifications.get("raw_data")

            raw_data_file_name_template = raw_data_info.get("file_name", "")
            raw_data_file_text_template = raw_data_info.get("text", "")
            raw_data_file_name = raw_data_file_name_template.format(entity_name=entity_name)
            raw_data_file_text = raw_data_file_text_template.format(entity_name=entity_name)

            code_file_name_template = code_info.get("file_name", "")
            code_file_text_template = code_info.get("text", "")
            code_file_name = code_file_name_template.format(entity_name=entity_name)
            code_file_text = code_file_text_template.format(entity_name=entity_name)

            doc_file_name_template = doc_info.get("file_name", "")
            doc_file_text_template = doc_info.get("text", "")
            doc_file_name = doc_file_name_template.format(entity_name=entity_name)
            doc_file_text = doc_file_text_template.format(entity_name=entity_name)

            entity_file_name_template = entity_info.get("file_name", "")
            entity_file_text_template = entity_info.get("text", "")
            entity_file_name = entity_file_name_template.format(entity_name=entity_name)
            entity_file_text = entity_file_text_template.format(entity_name=entity_name)

            code_file_path = os.path.join(target_dir, code_file_name)
            doc_file_path = os.path.join(target_dir, doc_file_name)
            entity_file_path = os.path.join(target_dir, entity_file_name)

            doc_file_text = await read_file(doc_file_path)
            entity_file_text = await read_file(entity_file_path)

            # notification_text = _event.get("notification_text").format(file_name=file_name)
            # await _send_notification_with_file(chat=chat, event=_event, notification_text=notification_text,
            #                                    file_name=file_name, editable=True)

        except Exception as e:
            logger.error(f"Unexpected error for entity {entity.get("entity_name")}: {e}")
            logger.exception(e)


def main():
    if __name__ == "__main__":
        resp = "test ```json\n{\n  \"name\": \"hello_world_workflow\",\n  \"description\": \"A simple workflow to send a Hello World email.\",\n  \"workflow_criteria\": {\n    \"externalized_criteria\": [],\n    \"condition_criteria\": []\n  },\n  \"transitions\": [\n    {\n      \"name\": \"send_email\",\n      \"description\": \"Triggered by a scheduled job to send a Hello World email.\",\n      \"start_state\": \"None\",\n      \"start_state_description\": \"Initial state before sending email.\",\n      \"end_state\": \"email_sent\",\n      \"end_state_description\": \"Email has been successfully sent.\",\n      \"automated\": true,\n      \"transition_criteria\": {\n        \"externalized_criteria\": [],\n        \"condition_criteria\": []\n      },\n      \"processes\": {\n        \"schedule_transition_processors\": [],\n        \"externalized_processors\": [\n          {\n            \"name\": \"send_hello_world_email\",\n            \"description\": \"Process to send a Hello World email.\",\n            \"calculation_nodes_tags\": \"3d1da699-c188-11ef-bd5b-40c2ba0ac9eb\",\n            \"attach_entity\": false,\n            \"calculation_response_timeout_ms\": \"5000\",\n            \"retry_policy\": \"FIXED\",\n            \"sync_process\": true,\n            \"new_transaction_for_async\": false,\n            \"none_transactional_for_async\": false,\n            \"processor_criteria\": {\n              \"externalized_criteria\": [],\n              \"condition_criteria\": []\n            }\n          }\n        ]\n      }\n    }\n  ]\n}\n``` test"
        resp = "{'name': 'send_hello_world_email_workflow', 'description': \"Workflow to send a 'Hello World' email at a scheduled time.\", 'workflow_criteria': {'externalized_criteria': [], 'condition_criteria': []}, 'transitions': [{'name': 'scheduled_send_email', 'description': \"Triggered by a schedule to send a 'Hello World' email.\", 'start_state': 'None', 'start_state_description': 'Initial state before the email is sent.', 'end_state': 'email_sent', 'end_state_description': 'Email has been successfully sent.', 'automated': True, 'transition_criteria': {'externalized_criteria': [], 'condition_criteria': []}, 'processes': {'schedule_transition_processors': [], 'externalized_processors': [{'name': 'send_email_process', 'description': \"Process to send 'Hello World' email at 5 PM every day.\", 'calculation_nodes_tags': 'd0ada585-c201-11ef-8296-40c2ba0ac9eb', 'attach_entity': True, 'calculation_response_timeout_ms': '5000', 'retry_policy': 'NONE', 'sync_process': True, 'new_transaction_for_async': False, 'none_transactional_for_async': False, 'processor_criteria': {'externalized_criteria': [], 'condition_criteria': []}}]}}]}"
        res = parse_json(resp)
        print(parse_json(resp))
        print(json.dumps(parse_json(resp)))


if __name__ == "__main__":
    main()
