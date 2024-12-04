import queue
from uuid import uuid1

from common.ai.ai_assistant_service import AiAssistantService
from common.auth.auth import authenticate

chat_id = uuid1()
question_queue = queue.Queue()
cyoda_token = authenticate()
ai_service = AiAssistantService()