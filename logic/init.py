import queue
from uuid import uuid1

from common.ai.ai_assistant_service import AiAssistantService
from common.auth.auth import authenticate
from common.repository.in_memory_db import InMemoryRepository
from common.service.service import EntityServiceImpl

cyoda_token = authenticate()
ai_service = AiAssistantService()
entity_repository = InMemoryRepository()
entity_service = EntityServiceImpl(entity_repository)