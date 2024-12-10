import logging
from typing import Dict, Any

from common.config.config import CYODA_AI_API, ENTITY_VERSION
from entity.workflow import dispatch_function
from entity.chat.workflow.helper_functions import _get_event_template, _chat
from logic.init import cyoda_token, entity_service
from logic.notifier import clients_queue

QUESTION_OR_VALIDATE = "Please answer the question or validate"

# Constants
CAN_PROCEED = "can_proceed"
PROMPT = "prompt"
ANSWER = "answer"
FUNCTION = "function"
QUESTION = "question"
NOTIFICATION = "notification"
# Setup logging
logger = logging.getLogger(__name__)

# def question(event: Dict[str, Any], stack) -> None:
#     """Enqueue a question event."""
#     question_queue.put(event)

def process_answer(_event: Dict[str, Any], chat) -> None:
    """
    Process an answer event by interacting with the chat service and managing the event stack.
    """
    result = _chat(_event=_event, token=cyoda_token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    question_event = _get_event_template(question=result, prompt='', max_iteration=0, notification='')
    stack = chat["chat_flow"]["current_flow"]
    if isinstance(result, dict) and result.get(CAN_PROCEED) is not None and result.get(CAN_PROCEED) is False and _event.get("iteration", 0) < _event.get("max_iteration", 0):
        _event["iteration"] += 1
        stack.append(_event)
        stack.append({QUESTION: QUESTION_OR_VALIDATE})
        stack.append(question_event)
    else:
        notification_event = _get_event_template(notification=result, prompt='', max_iteration=0, question = '')
        stack.append(notification_event)
        stack.append({NOTIFICATION: "Finishing iteration with result: "})


async def process_dialogue_script(token, technical_id) -> None:
    chat = entity_service.get_item(token=token,
                                   entity_model="chat",
                                   entity_version=ENTITY_VERSION,
                                   technical_id=technical_id)
    stack = chat["chat_flow"]["current_flow"]
    finished_stack = chat["chat_flow"]["finished_flow"]
    while stack and not stack[-1].get(QUESTION):
        event = stack.pop()
        finished_stack.append(event)
        if event.get(FUNCTION):
            dispatch_function(event, chat)
        elif event.get(PROMPT):
            process_answer(event, chat)
        elif event.get(NOTIFICATION):
            chat["questions_queue"]["new_questions"].put(event)
            await clients_queue.put(technical_id)

    while (stack and (stack[-1].get(QUESTION) or stack[-1].get(NOTIFICATION))):
        event = stack.pop()
        finished_stack.append(event)
        chat["questions_queue"]["new_questions"].put(event)
        await clients_queue.put(technical_id)

    entity_service.update_item(token=token,
                            entity_model="chat",
                            entity_version=ENTITY_VERSION,
                            technical_id=technical_id,
                            entity=chat,
                            meta={})
