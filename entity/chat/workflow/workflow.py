import logging
import os
from typing import Dict, Any

import aiofiles

from common.config.config import PROJECT_DIR, REPOSITORY_NAME, MAX_ITERATION
from common.util.utils import  git_pull,  _save_file,  parse_from_string

from entity.workflow import Workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entry_point_to_stack = {
}


class ChatWorkflow(Workflow):
    def __init__(self, entity_service, mock=False):
        self.entity_service = entity_service
        self.mock = mock

    async def save_file(self, technical_id, entity, **params) -> str:
        """
        Saves data to a file using the provided chat id and file name.
        """
        try:
            new_content = parse_from_string(escaped_code=params.get("new_content"))
            await _save_file(chat_id=technical_id, _data=new_content, item=params.get("filename"))
            return "File saved successfully"
        except Exception as e:
            return f"Error during saving file: {e}"

    async def read_file(self, technical_id, entity, **params) -> str:
        """
        Reads data from a file using the provided chat id and file name.
        """
        # Await the asynchronous git_pull function.
        await git_pull(chat_id=technical_id)

        target_dir = os.path.join(f"{PROJECT_DIR}/{technical_id}/{REPOSITORY_NAME}", "")
        file_path = os.path.join(target_dir, params.get("filename"))
        try:
            async with aiofiles.open(file_path, 'r') as file:
                content = await file.read()
            return content
        except FileNotFoundError:
            return ''
        except Exception as e:
            logger.exception("Error during reading file")
            return f"Error during reading file: {e}"

    async def set_additional_question_flag(self, technical_id: str, entity: Dict[str, Any], **params: Any) -> None:
        transition = params.get("transition")
        if transition is None:
            raise ValueError("Missing required parameter: 'transition'")

        additional_flag = params.get("require_additional_question_flag")

        # Ensure the nested dictionary for conditions exists.
        transitions = entity.setdefault("transitions", {})
        conditions = transitions.setdefault("conditions", {})

        # Set the flag for the specified transition.
        conditions.setdefault(transition, {})["require_additional_question"] = additional_flag

    async def is_stage_completed(self, technical_id: str, entity: Dict[str, Any], **params: Any) -> bool:
        transition = params.get("transition")
        if transition is None:
            raise ValueError("Missing required parameter: 'transition'")

        transitions = entity.get("transitions", {})
        current_iteration = transitions.get("current_iteration", {})
        max_iteration = transitions.get("max_iteration", {})

        if transition in current_iteration:
            allowed_max = max_iteration.get(transition, MAX_ITERATION)
            if current_iteration[transition] > allowed_max:
                return True

        conditions = transitions.get("conditions", {})
        # If the condition for the transition does not exist, assume stage is not completed.
        if transition not in conditions:
            return False

        # Return the inverse of the require_additional_question flag.
        return not conditions[transition].get("require_additional_question", True)

