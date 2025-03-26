import asyncio
import os

from common.ai.ai_agent import OpenAiAgent
from common.ai.clients.openai_client import AsyncOpenAIClient
from common.config.config import CHAT_REPOSITORY
from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.repository.in_memory_db import InMemoryRepository
from common.service.service import EntityServiceImpl
from entity.chat.workflow.flow_processor import FlowProcessor
from entity.chat.workflow.workflow import ChatWorkflow
from entity.workflow import Workflow
from entity.workflow_dispatcher import WorkflowDispatcher


class BeanFactory:
    def __init__(self, config=None):
        """
        Initialize the dependency container. You can pass a configuration dictionary,
        or rely on environment variables/default values.
        """
        # Load configuration, allowing overrides via environment or parameter.
        # Initialize asynchronous lock (e.g., for handling concurrent chat operations)
        self.chat_lock = asyncio.Lock()

        try:
            # Create the repository based on configuration.
            self.dataset = {}
            self.device_sessions = {}
            self.workflow = Workflow()
            self.entity_repository = self._create_repository(CHAT_REPOSITORY)
            self.entity_service = EntityServiceImpl(repository=self.entity_repository)

            self.chat_workflow = ChatWorkflow(
                entity_service=self.entity_service
            )
            self.openai_client = AsyncOpenAIClient()
            self.ai_agent = OpenAiAgent(client=self.openai_client)

            self.workflow_dispatcher = WorkflowDispatcher(
                cls=ChatWorkflow,
                cls_instance=self.chat_workflow,
                ai_agent=self.ai_agent,
            )
            self.flow_processor = FlowProcessor(
                workflow_dispatcher=self.workflow_dispatcher
            )



        except Exception as e:
            # Replace print with a proper logging framework in production.
            print("Error during BeanFactory initialization:", e)
            raise

    def _load_default_config(self):
        """
        Load default configuration values, optionally from environment variables.
        """
        return {
            "CHAT_REPOSITORY": os.getenv("CHAT_REPOSITORY", "inmemory")
        }

    def _create_repository(self, repo_type):
        """
        Create the appropriate repository based on configuration.
        """
        if repo_type.lower() == "cyoda":
            return CyodaRepository()
        else:
            return InMemoryRepository()

    def get_flow_processor(self):
        """
        Retrieve the FlowProcessor instance.
        """
        return self.flow_processor

    def get_services(self):
        """
        Retrieve a dictionary of all managed services for further use.
        """
        return {
            "chat_lock": self.chat_lock,
            "entity_repository": self.entity_repository,
            "entity_service": self.entity_service,
            "ai_agent": self.ai_agent,
            "workflow": self.workflow,
            "chat_workflow": self.chat_workflow,
            "workflow_dispatcher": self.workflow_dispatcher,
            "flow_processor": self.flow_processor,
            "dataset": self.dataset,
            "device_sessions": self.device_sessions,
        }


# Example usage:
if __name__ == "__main__":
    # Optional: Define a custom configuration (this can also be managed externally)
    config = {
        "CHAT_REPOSITORY": "cyoda"  # Change to "inmemory" if desired
    }
    factory = BeanFactory(config=config)
    flow_processor = factory.get_flow_processor()

    # Now you can use flow_processor and other services as needed in your application.
    print("BeanFactory initialized successfully. FlowProcessor is ready to use.")
