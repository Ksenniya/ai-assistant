
import unittest
from unittest.mock import patch, MagicMock
import sys

# Assuming your app.py is in the parent directory
sys.path.append("..")

from logic.logic import (
    question,
    process_answer,
    process_dialogue_script,
    question_queue,
    stack, QUESTION_OR_VALIDATE
)

class TestAppFunctions(unittest.TestCase):
    def setUp(self):
        # Reset the queue and stack before each test
        while not question_queue.empty():
            question_queue.get()
        stack.clear()


    def test_question_enqueues_event(self):
        """Test that the question function enqueues the event."""
        event = {"prompt": "Test Prompt", "answer": "Test Answer"}
        question(event)
        self.assertFalse(question_queue.empty())
        queued_event = question_queue.get()
        self.assertEqual(queued_event, event)

    @patch('logic.app_helper_functions._chat')
    def test_process_answer_can_proceed_false_within_max_iteration(self, mock_chat):
        """Test process_answer when can_proceed is False and within max_iteration."""
        mock_chat.return_value = {"can_proceed": False}
        event = {
            "prompt": "Test Prompt",
            "answer": "Test Answer",
            "mock_answer": "Mock Answer",
            "iteration": 1,
            "max_iteration": 3,
            "function": None
        }

        process_answer(event)

        # Verify that chat was called correctly
        mock_chat.assert_called_with("Test Prompt: Test Answer", "Mock Answer")

        # Check that the stack was updated correctly
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack[-3], event)  # Original event with incremented iteration
        self.assertEqual(stack[-2], {"question": QUESTION_OR_VALIDATE})
        self.assertEqual(stack[-1], {
            "question": {"can_proceed": False},
            "prompt": "",
            "answer": "",
            "function": None,
            "index": 0,
            "iteration": 0,
            "max_iteration": 0
        })

    @patch('logic.app_helper_functions._chat')
    def test_process_answer_can_proceed_true(self, mock_chat):
        """Test process_answer when can_proceed is True."""
        mock_chat.return_value = {"can_proceed": True}
        event = {
            "prompt": "Test Prompt",
            "answer": "Test Answer",
            "mock_answer": "Mock Answer",
            "iteration": 1,
            "max_iteration": 3,
            "function": None
        }

        with patch('logic.app_logic.question') as mock_question:
            process_answer(event)

            # Verify that chat was called correctly
            mock_chat.assert_called_with("Test Prompt: Test Answer", "Mock Answer")

            # Verify that question was called with the new question_event
            mock_question.assert_called_once_with({
                "question": {"can_proceed": True},
                "prompt": "",
                "answer": "",
                "function": None,
                "index": 0,
                "iteration": 0,
                "max_iteration": 0
            })

            # Ensure the stack was not modified
            self.assertEqual(len(stack), 0)

    @patch('logic.app_helper_functions._chat')
    def test_process_answer_iteration_exceeds_max(self, mock_chat):
        """Test process_answer when can_proceed is False but iteration exceeds max_iteration."""
        # Mock the chat function to return can_proceed as False
        mock_chat.return_value = {"can_proceed": False}

        # Create an event where iteration exceeds max_iteration
        event = {
            "prompt": {
                "text": "Improve the Cyoda design based on the user answer if the user wants any improvements",
                "schema": {}
            },
            "answer": "AI ethics involves...",
            "mock_answer": "Mock response",
            "iteration": 4,  # Set iteration > max_iteration
            "max_iteration": 3,
            "function": {
                "name": "function_name",
                "prompt": {
                    "text": "test_text",
                    "schema": {}
                }
            }
        }

        # Patch the question function to monitor its calls
        with patch('logic.app_logic.question') as mock_question:
            # Call the process_answer function with the event
            process_answer(event)

            # Verify that chat was called with the correct arguments
            mock_chat.assert_called_with("Explain AI ethics: AI ethics involves...", "Mock response")

            # Verify that question was called once with the expected question_event
            mock_question.assert_called_once_with({
                "question": {"can_proceed": False},
                "prompt": "",
                "answer": "",
                "function": None,
                "index": 0,
                "iteration": 0,
                "max_iteration": 0
            })

            # Ensure that the stack was not modified (no items should be appended)
            self.assertEqual(len(stack), 0)

    def test_process_dialogue_script_empty_stack(self):
        """Test process_dialogue_script with an empty stack."""
        with self.assertLogs('logic.app_logic', level='INFO') as log:
            process_dialogue_script()
            self.assertIn('Finished', log.output[0])

    @patch('logic.app_logic.dispatch_function')
    def test_process_dialogue_script_with_function_event(self, mock_dispatch):
        """Test process_dialogue_script handling function events."""
        event = {
            "function": "some_function",
            "prompt": "",
            "question": ""
        }
        stack.append(event)

        process_dialogue_script()

        # Verify that dispatch_function was called with the event
        mock_dispatch.assert_called_once_with(event)
        self.assertEqual(len(stack), 0)

    @patch('logic.app_logic.process_answer')
    def test_process_dialogue_script_with_prompt_event(self, mock_process_answer):
        """Test process_dialogue_script handling prompt events."""
        event = {
            "prompt": "Test Prompt",
            "answer": "Test Answer",
            "question": ""
        }
        stack.append(event)

        process_dialogue_script()

        # Verify that process_answer was called with the event
        mock_process_answer.assert_called_once_with(event)
        self.assertEqual(len(stack), 0)

    def test_process_dialogue_script_with_question_event(self):
        """Test process_dialogue_script handling question events."""
        event = {
            "question": {"can_proceed": True},
            "prompt": "",
            "answer": "",
            "function": None
        }
        stack.append(event)

        with patch('logic.app_logic.question') as mock_question:
            process_dialogue_script()

            # Verify that question was called with the event
            mock_question.assert_called_once_with(event)
            self.assertEqual(len(stack), 0)

    @patch('logic.app_helper_functions._chat')
    @patch('logic.app_logic.logging.error')
    def test_process_answer_exception_handling(self, mock_logging_error, mock_chat):
        """Test that process_answer handles exceptions from chat."""
        # Configure the chat mock to raise an exception
        mock_chat.side_effect = Exception("Chat service failed")

        event = {
            "prompt": "Test Prompt",
            "answer": "Test Answer",
            "mock_answer": "Mock Answer",
            "iteration": 1,
            "max_iteration": 3,
            "function": None
        }

        process_answer(event)

        # Verify that chat was called with correct arguments
        mock_chat.assert_called_once_with("Test Prompt: Test Answer", "Mock Answer")

        # Verify that logging.error was called once with the correct message
        mock_logging_error.assert_called_once_with("Error processing answer: Chat service failed")

        # Ensure that the stack was not modified due to the exception
        self.assertEqual(len(stack), 0)

    @patch('logic.app_logic.dispatch_function')
    def test_process_dialogue_script_multiple_events(self, mock_dispatch):
        """Test process_dialogue_script with multiple events in the stack."""
        func_event = {"function": "func1", "prompt": "", "question": ""}
        prompt_event = {"prompt": "Prompt1", "answer": "Answer1", "question": ""}
        question_event = {"question": "Question1", "prompt": "", "answer": "", "function": None}

        stack.extend([func_event, prompt_event, question_event])

        with patch('logic.app_logic.dispatch_function') as mock_dispatch, \
                patch('logic.app_logic.process_answer') as mock_process_answer, \
                patch('logic.app_logic.question') as mock_question:
            process_dialogue_script()

            # Verify that dispatch_function was called with func_event
            mock_dispatch.assert_called_once_with(func_event)

            # Verify that process_answer was called with prompt_event
            mock_process_answer.assert_called_once_with(prompt_event)

            # Verify that question was called with question_event
            mock_question.assert_called_once_with(question_event)

            # Ensure the stack is empty
            self.assertEqual(len(stack), 0)

if __name__ == '__main__':
    unittest.main()