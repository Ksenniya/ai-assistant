import logging
from typing import Dict, Any

from common.config.config import CYODA_AI_API, ENTITY_VERSION
from entity.workflow import dispatch_function
from entity.chat.workflow.helper_functions import _get_event_template, _chat, _save_result_to_file
from logic.init import cyoda_token, entity_service
from logic.notifier import clients_queue

QUESTION_OR_VALIDATE = "Could you please help me review my output and approve it you are happy with the result ^-^"

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

def process_answer(token, _event: Dict[str, Any], chat) -> None:
    """
    Process an answer event by interacting with the chat service and managing the event stack.
    """
    stack = chat["chat_flow"]["current_flow"]
    if _event.get("iteration", 0) > _event.get("max_iteration", 0):
        stack.append({NOTIFICATION: "Finishing iteration"})
        return
    else:
        result = _chat(chat=chat, _event=_event, token=cyoda_token,
                       ai_endpoint=_event.get("prompt", {}).get("api", CYODA_AI_API),
                       chat_id=chat["chat_id"])

        question_event = _get_event_template(question=result, event=_event, notification='', answer='', prompt={})

        if repeat_iteration(_event, result):
            _event["iteration"] += 1
            stack.append(_event)
            stack.append({QUESTION: QUESTION_OR_VALIDATE})
            stack.append(question_event)
        else:
            notification_event = _get_event_template(notification=result, event=_event, question='', answer='', prompt={})
            stack.append(notification_event)
            stack.append({NOTIFICATION: "Finishing iteration with result: "})
        if _event.get("prompt", {}).get("function", ''):
            function_event = _get_event_template(event=_event, notification='', answer='', prompt={}, question='')
            dispatch_function(token, function_event, chat)
        _save_result_to_file(chat=chat, _event=_event, data=result)


def repeat_iteration(_event, result):
    iteration = _event.get("iteration", 0)
    max_iteration = _event.get("max_iteration", 0)
    # Safely extract can_proceed only if `result` is a dict
    if isinstance(result, dict):
        can_proceed = result.get(CAN_PROCEED)  # could be True, False, or None
    else:
        can_proceed = None
    # Construct the condition piece by piece for clarity
    has_valid_can_proceed = (can_proceed is not None)
    needs_initial_iteration = (iteration == 0 and max_iteration > 0)
    cannot_proceed = (can_proceed is False or needs_initial_iteration)
    has_remaining_iterations = (iteration < max_iteration)
    return has_valid_can_proceed and cannot_proceed and has_remaining_iterations


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
            dispatch_function(token, event, chat)
        elif event.get(PROMPT):
            process_answer(token, event, chat)
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
