import logging
from typing import Dict, Any

from common.config.config import CYODA_AI_API, ENTITY_VERSION
from common.config.conts import NOTIFICATION, QUESTION, FUNCTION, PROMPT, CAN_PROCEED
from entity.workflow import dispatch_function
from entity.chat.workflow.helper_functions import get_event_template, save_result_to_file, run_chat
from logic.init import cyoda_token, entity_service
from logic.notifier import clients_queue



# Setup logging
logger = logging.getLogger(__name__)


# def question(event: Dict[str, Any], stack) -> None:
#     """Enqueue a question event."""
#     question_queue.put(event)

async def process_answer(token, _event: Dict[str, Any], chat) -> None:
    """
    Process an answer event by interacting with the chat service and managing the event stack.
    """
    stack = chat["chat_flow"]["current_flow"]
    if _event.get("iteration", 0) > _event.get("max_iteration", 0):
         return
    result = await run_chat(chat=chat, _event=_event, token=cyoda_token,
                  ai_endpoint=_event.get("prompt", {}).get("api", CYODA_AI_API),
                  chat_id=chat["chat_id"])

    question_event = get_event_template(question=result, event=_event, notification='', answer='', prompt={})

    if repeat_iteration(_event, result):
        _event["iteration"] += 1
        stack.append(_event)
        if _event.get("additional_questions"):
            for additional_question in _event.get("additional_questions", [])[::-1]:
                stack.append({QUESTION: additional_question})
        stack.append(question_event)
    else:
        notification_event = get_event_template(notification=result, event=_event, question='', answer='', prompt={})
        stack.append(notification_event)
        #stack.append({NOTIFICATION: "🎉 We're wrapping up this iteration with result: "})
    if _event.get("prompt", {}).get("function", ''):
        function_event = get_event_template(event=_event, notification='', answer='', prompt={}, question='')
        await dispatch_function(token, function_event, chat)
    await save_result_to_file(chat=chat, _event=_event, _data=result)


def repeat_iteration(_event, result):
    iteration = _event.get("iteration", 0)
    max_iteration = _event.get("max_iteration", 0)
    # Safely extract can_proceed only if `result` is a dict
    if isinstance(result, dict):
        can_proceed = result.get(CAN_PROCEED)  # could be True, False, or None
    else:
        can_proceed = False
    # Construct the condition piece by piece for clarity
    # has_valid_can_proceed = (can_proceed is not None)
    # if has_valid_can_proceed:
    #     can_proceed = False
    needs_initial_iteration = (iteration == 0 and max_iteration > 0)
    cannot_proceed = (can_proceed is False or needs_initial_iteration)
    has_remaining_iterations = (iteration < max_iteration)
    return cannot_proceed and has_remaining_iterations


async def process_dialogue_script(token, technical_id) -> None:
    chat = await entity_service.get_item(token=token,
                                   entity_model="chat",
                                   entity_version=ENTITY_VERSION,
                                   technical_id=technical_id)
    stack = chat["chat_flow"]["current_flow"]
    finished_stack = chat["chat_flow"].get("finished_flow", [])
    while stack and not stack[-1].get(QUESTION):
        event = stack.pop()
        finished_stack.append(event)
        if event.get(FUNCTION):
            await dispatch_function(token, event, chat)
        elif event.get(PROMPT):
            await process_answer(token, event, chat)
        elif event.get(NOTIFICATION):
            if "questions_queue" not in chat:
                chat["questions_queue"] = {}

            if "new_questions" not in chat["questions_queue"]:
                chat["questions_queue"]["new_questions"] = []

            # Now append the event to the list
            chat["questions_queue"]["new_questions"].append(event)

    while stack and (stack[-1].get(QUESTION) or stack[-1].get(NOTIFICATION)):
        event = stack.pop()
        finished_stack.append(event)
        if "questions_queue" not in chat:
            chat["questions_queue"] = {}

        if "new_questions" not in chat["questions_queue"]:
            chat["questions_queue"]["new_questions"] = []

        # Now append the event to the list
        chat["questions_queue"]["new_questions"].append(event)

    await entity_service.update_item(token=token,
                               entity_model="chat",
                               entity_version=ENTITY_VERSION,
                               technical_id=technical_id,
                               entity=chat,
                               meta={})
