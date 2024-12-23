import json
import logging

from common.config.config import CYODA_AI_URL, MOCK_AI, CYODA_AI_API, WORKFLOW_AI_API, CONNECTION_AI_API, RANDOM_AI_API
from common.util.utils import parse_json, validate_result, send_post_request

API_V_CONNECTIONS_ = "api/v1/connections"
API_V_CYODA_ = "api/v1/cyoda"
API_V_WORKFLOWS_ = "api/v1/workflows"
API_V_RANDOM_ = "api/v1/random"
logger = logging.getLogger(__name__)

class AiAssistantService:
    def __init__(self):
        pass

    def init_chat(self, token, chat_id):
        if MOCK_AI=="true":
            return {"success": True}
        data = json.dumps({"chat_id": f"{chat_id}"})
        endpoints = [API_V_CYODA_, API_V_WORKFLOWS_, API_V_CONNECTIONS_, API_V_RANDOM_]
        for endpoint in endpoints:
            send_post_request(token, CYODA_AI_URL, "%s/initial" % endpoint, data)
        return {"success": True}

    def init_workflow_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_WORKFLOWS_, data)
        return resp.json()

    def init_connections_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_CONNECTIONS_, data)
        return resp.json()

    def init_random_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_RANDOM_, data)
        return resp.json()

    def ai_chat(self, token, chat_id, ai_endpoint, ai_question):
        if MOCK_AI=="true":
            return {"entity": "some random text"}
        if ai_endpoint == CYODA_AI_API:
            resp = self.chat_cyoda(token=token, chat_id=chat_id, ai_question=ai_question)
            return resp["message"]
        if ai_endpoint == WORKFLOW_AI_API:
            resp = self.chat_workflow(token=token, chat_id=chat_id, ai_question=ai_question)
            return resp["message"]
        if ai_endpoint == CONNECTION_AI_API:
            resp = self.chat_connection(token=token, chat_id=chat_id, ai_question=ai_question)
            return resp["message"]
        if ai_endpoint == RANDOM_AI_API:
            resp = self.chat_random(token=token, chat_id=chat_id, ai_question=ai_question)
            return resp["message"]

    def chat_cyoda(self, token, chat_id, ai_question):
        data = json.dumps({"chat_id": f"{chat_id}", "question": f"{ai_question}"})
        resp = send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_CYODA_, data)
        return resp.json()



    def chat_workflow(self, token, chat_id, ai_question):
        data = json.dumps({
            "question": f"{ai_question}",
            "return_object": "workflow",
            "chat_id": f"{chat_id}",
            "class_name": "com.cyoda.tdb.model.treenode.TreeNodeEntity"
        })
        resp = send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_WORKFLOWS_, data)
        return resp.json()

    def export_workflow_to_cyoda_ai(self, token, chat_id, data):
        try:
            data = json.dumps({
                "name": data["name"],
                "chat_id": chat_id,
                "class_name": data["class_name"],
                "transitions": data["transitions"]
            })
            resp = send_post_request(token, CYODA_AI_URL, "%s/generate-workflow" % API_V_WORKFLOWS_, data)
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to export workflow: {e}")

    def validate_and_parse_json(self, token:str, chat_id: str, data: str, schema: str, ai_endpoint:str, max_retries: int):
        try:
            parsed_data = parse_json(data)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError("Invalid JSON entity provided.") from e

        attempt = 0
        while attempt <= max_retries:
            try:
                parsed_data = validate_result(parsed_data, '', schema)
                logger.info(f"JSON validation successful on attempt {attempt + 1}.")
                return parsed_data
            except Exception as e:
                logger.warning(
                    f"JSON validation failed on attempt {attempt + 1} with error: {e}"
                )
                if attempt < max_retries:
                    question = (
                        f"Retry the last step. JSON validation failed with error: {e}. "
                        "Return only the DTO JSON."
                    )
                    retry_result = self.ai_chat(token=token, chat_id=chat_id, ai_endpoint=ai_endpoint, ai_question=question)
                    parsed_data = parse_json(retry_result)
            finally:
                attempt += 1
        logger.error(f"Maximum retry attempts reached. Validation failed. Attempt: {attempt}")
        raise ValueError("JSON validation failed after retries.")


    def chat_connection(self, token, chat_id, ai_question):
        data = json.dumps({
            "question": f"{ai_question}",
            "return_object": "import-connections",
            "chat_id": f"{chat_id}"
        })
        resp = send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_CONNECTIONS_, data)
        return resp.json()


    def chat_random(self, token, chat_id, ai_question):
        data = json.dumps({
            "question": f"{ai_question}",
            "return_object": "random",
            "chat_id": f"{chat_id}"
        })
        resp = send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_CONNECTIONS_, data)
        return resp.json()