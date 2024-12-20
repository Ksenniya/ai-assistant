import unittest

from entity.chat.workflow.helper_functions import _enrich_prompt_with_context


class TestEnrichPromptWithContext(unittest.TestCase):

    def setUp(self):
        # Common test setup data
        self._event = {
            'context': {'code': ['UHwZUhHx0H', 'code']}
        }

        self.chat = {
            'cache': {
                'UHwZUhHx0H': {'code': [{'ingest_data': 'TvyeK9CfTY12'}]},
                'other_key': 'SomeOtherValue'
            }
        }

        self.event_prompt = {
            'text': 'Generate the processor functions for $code with the processors in each transition.'
        }

    def test_basic_replacement(self):
        # Test with a valid context replacement
        prompt = _enrich_prompt_with_context(self._event, self.chat, self.event_prompt)
        expected = "Generate the processor functions for [{'ingest_data': 'TvyeK9CfTY12'}] with the processors in each transition."
        self.assertEqual(prompt, expected)


if __name__ == '__main__':
    unittest.main()