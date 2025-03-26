import json
import logging
from openai.types.chat.chat_completion import ChatCompletionMessage

from common.util.utils import _save_file

# Setup logging
logger = logging.getLogger(__name__)


class FlowProcessor:
    def __init__(self, workflow_dispatcher, mock=False):
        self.workflow_dispatcher = workflow_dispatcher
        self.mock = mock

    async def run_workflow(self, fsm, entity, technical_id, current_state=None):
        if current_state is None:
            current_state = fsm["initial_state"]
        while True:
            state_info = fsm["states"].get(current_state)
            if not state_info:
                logger.info(f"State '{current_state}' is not defined in FSM.")
                break

            transitions = state_info.get("transitions", {})
            auto_transition_taken = False

            for event, transition in transitions.items():
                # Skip manual transitions when running automatically.
                if transition.get("manual", False):
                    logger.info(f"Manual transition available from state '{current_state}' on event '{event}'.")
                    continue

                # Check the condition, if any.
                if "condition" in transition:
                    cond_func = await self.workflow_dispatcher.process_event(token="test",
                                                                             entity=entity,
                                                                             technical_id=technical_id,
                                                                             action=transition["condition"])
                    if not cond_func:
                        continue

                # Execute the action if defined.
                if "action" in transition:
                    result = await self.workflow_dispatcher.process_event(token="test",
                                                                          entity=entity,
                                                                          technical_id=technical_id,
                                                                          action=transition["action"])

                # Transition to the next state.
                next_state = transition["next"]
                logger.info(f"Auto-transition: from '{current_state}' to '{next_state}' via event '{event}'.")
                current_state = next_state
                auto_transition_taken = True
                break  # Process one transition at a time.

            if not auto_transition_taken:
                logger.info(f"No applicable automatic transitions from state '{current_state}'.")
                break
        entity["current_state"]=current_state
        entity["transition"] = event
        await _save_file(chat_id=technical_id, _data=json.dumps(entity, cls=ChatCompletionMessageEncoder), item="entity/chat.json")
        return current_state

    async def trigger_manual_transition(self, current_state, event, entity, fsm, technical_id):
        """
        Triggers a manual transition from the current state for a given event.

        :param current_state: The current state's name.
        :param event: The event to trigger (must be defined as manual in the FSM).
        :param entity: Data used to evaluate conditions.
        :param fsm: The FSM configuration dictionary.
        :return: The new state after the manual transition.
        """
        try:
            state_info = fsm["states"].get(current_state)
            if not state_info:
                logger.info(f"State '{current_state}' is not defined in FSM.")
                entity["current_state"] = current_state
                return current_state

            transitions = state_info.get("transitions", {})
            transition = transitions.get(event)
            if not transition:
                logger.info(f"No transition defined for event '{event}' in state '{current_state}'.")
                entity["current_state"] = current_state
                return current_state

            if not transition.get("manual", False):
                logger.info(f"Transition for event '{event}' in state '{current_state}' is not manual.")
                entity["current_state"] = current_state
                return current_state

            # Check condition, if any.
            if "condition" in transition:
                cond_func = await self.workflow_dispatcher.process_event(token="test",
                                                                         entity=entity,
                                                                         technical_id=technical_id,
                                                                         action=transition["condition"])
                if not cond_func:
                    logger.info(
                        f"Condition '{transition['condition']}' not met for manual event '{event}' in state '{current_state}'.")
                    entity["current_state"] = current_state
                    return current_state

            # Execute the action if defined.
            if "action" in transition:
                result = await self.workflow_dispatcher.process_event(token="test",
                                                                      entity=entity,
                                                                      technical_id=technical_id,
                                                                      action=transition["action"])

            next_state = transition["next"]
            logger.info(f"Manual-triggered transition: from '{current_state}' to '{next_state}' via event '{event}'.")
            entity["current_state"] = next_state
        finally:
            current_state = await self.run_workflow(fsm=fsm,
                                                    entity=entity,
                                                    technical_id=technical_id,
                                                    current_state=entity["current_state"])
            entity["current_state"] = current_state
            entity["transition"] = event
            await _save_file(chat_id=technical_id, _data=json.dumps(entity, cls=ChatCompletionMessageEncoder), item="entity/chat.json")
            return current_state

class ChatCompletionMessageEncoder(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, dict):
            # Convert the object to a dictionary. Customize as needed.
            return o.__dict__
        return super().default(o)