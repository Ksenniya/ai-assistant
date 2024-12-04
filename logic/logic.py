import logging
from typing import Dict, Any

from common.config.config import CYODA_AI_API
from entity.app_builder_job.data.data import stack
from entity.workflow import dispatch_function
from entity.app_builder_job.workflow.helper_functions import _get_event_template, _chat
from logic.init import cyoda_token, chat_id, question_queue

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

def question(event: Dict[str, Any]) -> None:
    """Enqueue a question event."""
    question_queue.put(event)

def process_answer(_event: Dict[str, Any]) -> None:
    """
    Process an answer event by interacting with the chat service and managing the event stack.
    """
    result = _chat(_event=_event, token=cyoda_token, ai_endpoint=CYODA_AI_API, chat_id=chat_id)
    question_event = _get_event_template(question=result, prompt='', max_iteration=0)
    if isinstance(result, dict) and result.get(CAN_PROCEED) is not None and result.get(CAN_PROCEED) is False and _event.get("iteration", 0) < _event.get("max_iteration", 0):
        _event["iteration"] += 1
        stack.append(_event)
        stack.append({QUESTION: QUESTION_OR_VALIDATE})
        stack.append(question_event)
    else:
        question(question_event)


def process_dialogue_script() -> None:
    """Process the dialogue script by handling events from the stack."""
    if not stack:
        logger.info("Finished")
        return

    while stack and not stack[-1].get(QUESTION):
        event = stack.pop()
        if event.get(FUNCTION):
            dispatch_function(event)
        elif event.get(PROMPT):
            process_answer(event)
        elif event.get(NOTIFICATION):
            question(event)

    while (stack and (stack[-1].get(QUESTION) or stack[-1].get(NOTIFICATION))):
        event = stack.pop()
        question(event)
