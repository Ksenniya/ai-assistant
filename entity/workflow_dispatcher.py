import inspect
import logging
from common.config.conts import OPEN_AI
from common.util.utils import _save_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowDispatcher:
    def __init__(self, cls, cls_instance, ai_agent, mock=False):
        self.cls = cls
        self.cls_instance = cls_instance
        self.methods_dict = self.collect_subclass_methods()
        self.ai_agent = ai_agent

    def collect_subclass_methods(self):

        # Using inspect.getmembers ensures we only get functions defined on the class
        methods = {}
        for name, func in inspect.getmembers(self.cls,
                                             predicate=inspect.isfunction):
            # Create a unique key to avoid collisions
            key = f"{name}"
            methods[key] = func
        return methods

    async def dispatch_function(self, function_name, **params):
        try:
            if function_name in self.methods_dict:
                response = await self.methods_dict[function_name](self.cls_instance,
                                                                  **params)
            else:
                raise ValueError(f"Unknown processing step: {function_name}")
            return response
        except Exception as e:
            logger.exception(e)
            logger.info(f"Error processing event: {e}")

    async def process_event(self, token, entity, action, technical_id):
        response = "returned empty response"
        config = action.get("config")

        try:
            action_name = action.get("name")

            if config and config.get("type"):
                response = await self._handle_config_based_event(config=config,
                                                                 entity=entity,
                                                                 technical_id=technical_id)
            elif action_name in self.methods_dict:
                response = await self._execute_method(method_name=action_name,
                                                      technical_id=technical_id,
                                                      entity=entity)
            else:
                raise ValueError(f"Unknown processing step: {action_name}")

        except Exception as e:
            logger.exception(f"Exception occurred while processing event: {e}")

        logger.info(f"{action}: {response}")
        return response

    async def _execute_method(self, method_name, technical_id, entity):
        try:
            return await self.methods_dict[method_name](self.cls_instance,
                                                        technical_id=technical_id,
                                                        entity=entity)
        except Exception as e:
            logger.info(f"Error executing method '{method_name}': {e}")
            raise

    async def _handle_config_based_event(self, config, entity, technical_id):
        response = None
        finished_stack = entity["chat_flow"].get("finished_flow", [])
        config_type = config.get("type")

        if config_type in ("notification", "question"):
            questions_queue = entity.setdefault("questions_queue", {})
            new_questions = questions_queue.setdefault("new_questions", [])

            if config.get("publish"):
                new_questions.append(config)

        elif config_type == "function":
            params = config["function"].get("parameters", {})
            response = await self.methods_dict[config["function"]["name"]](self.cls_instance,
                                                                           technical_id=technical_id,
                                                                           entity=entity,
                                                                           **params)
        elif config_type in ("prompt", "agent", "batch"):
            response = await self.run_ai_agent(
                config=config,
                entity=entity,
                finished_stack=finished_stack,
                technical_id=technical_id
            )
        else:
            raise ValueError(f"Unknown config type: {config_type}")
        await self.finalize_response(technical_id=technical_id,
                                     config=config,
                                     entity=entity,
                                     finished_stack=finished_stack,
                                     response=response)
        return response

    async def run_ai_agent(self, config, entity, finished_stack, technical_id):
        if self._check_and_update_iteration(config=config, entity=entity):
            return "Let's proceed to the next iteration"
        self._append_messages(entity=entity, config=config, finished_stack=finished_stack)
        response = await self._get_ai_agent_response(config=config, entity=entity, technical_id=technical_id)
        return response

    def _check_and_update_iteration(self, config, entity):
        max_iteration = config.get("max_iteration")
        if max_iteration is None:
            return False
        transition = entity["transition"]
        iterations = entity["transitions"]["current_iteration"]
        if transition not in iterations:
            iterations[transition] = 0
            entity["transitions"]["max_iteration"][transition] = max_iteration
        current_iteration = iterations[transition]
        if current_iteration > max_iteration:
            return True
        iterations[transition] = current_iteration + 1
        return False

    def _append_messages(self, config, entity, finished_stack):
        messages = config.get("messages")
        if messages:
            entity["messages"].extend(messages)
        if finished_stack:
            latest_message = finished_stack[-1]
            if latest_message.get("type") == "answer" and not latest_message.get("consumed"):
                answer_content = latest_message.get("answer")
                entity["messages"].append({"role": "user", "content": answer_content})
                latest_message["consumed"] = True

    async def _get_ai_agent_response(self, config, entity, technical_id):

        return await self.ai_agent.run(
            methods_dict=self.methods_dict,
            cls_instance=self.cls_instance,
            entity=entity,
            technical_id=technical_id,
            tools=config.get("tools"),
            model=OPEN_AI,
            tool_choice=config.get("tool_choice")
        )

    async def finalize_response(self, technical_id, entity, config, finished_stack, response):

        finished_stack.append(config)

        if config["type"] in ("function", "prompt", "agent"):

            if response and response != "None":
                notification = {
                    "allow_anonymous_users": config.get("allow_anonymous_users", False),
                    "publish": config.get("publish", False),
                    "notification": f"{response}",
                    "approve": config.get("approve", False),
                    "type": "notification"
                }
                finished_stack.append(notification)
                if config.get("publish"):
                    entity["questions_queue"]["new_questions"].append(notification)

            await self.write_to_output(config=config,
                                       response=response,
                                       technical_id=technical_id)

    async def write_to_output(self, config, response, technical_id):
        if config.get("output"):
            if config.get("output").get("local_fs"):
                local_files = config.get("output").get("local_fs")
                for filename in local_files:
                    await _save_file(chat_id=technical_id, _data=response, item=filename)
