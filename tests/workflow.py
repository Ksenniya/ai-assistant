import unittest
from unittest.mock import AsyncMock
import json

from entity.chat.workflow.workflow import generate_data_ingestion_entities_template


class TestGenerateDataIngestionEntitiesTemplate(unittest.TestCase):

    def setUp(self):
        # Mock the external functions
        self.mock_save_file = AsyncMock()
        self.mock_send_notification_with_file = AsyncMock()

        # Create a basic event and chat object
        self._event = {
            "entities": [
                {"entity_name": "entity1"}
            ],
            "files_notifications": {
                "code": {
                    "file_name": "{entity_name}_code.txt",
                    "text": "Code file for {entity_name}"
                }
            }
        }
        self.chat = {"chat_id": "12345"}

    def test_basic_case(self):
        # Run the function with mocks
        # We pass the mocked functions as arguments
        async def run_test():
            await generate_data_ingestion_entities_template(
                token="dummy_token",
                _event=self._event,
                chat=self.chat
            )

        # Run the test asynchronously
        import asyncio
        asyncio.run(run_test())




if __name__ == "__main__":
    unittest.main()