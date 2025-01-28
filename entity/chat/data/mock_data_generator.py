import json
import os
import random
import string
from typing import Any, Dict

from common.config.config import NUM_MOCK_ARR_ITEMS
from entity.chat.data.data import entity_stack, app_building_stack as stack, workflow_stack, scheduler_stack, \
    form_submission_stack, file_upload_stack, api_request_stack, data_ingestion_stack


def generate_data_from_schema(schema: Dict[str, Any]) -> Any:
    schema_type = schema.get('type', 'object')

    if 'enum' in schema:
        return random.choice(schema['enum'])

    if schema_type == 'object':
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        if not properties:
            return {"a": "a1"}
        obj = {}
        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.choice([True, False]):
                obj[prop_name] = generate_data_from_schema(prop_schema)
        return obj

    elif schema_type == 'array':
        item_schema = schema.get('items', {})
        min_items = schema.get('minItems', NUM_MOCK_ARR_ITEMS)
        max_items = schema.get('maxItems', NUM_MOCK_ARR_ITEMS)
        num_items = random.randint(min_items, max_items)
        return [generate_data_from_schema(item_schema) for _ in range(num_items)]

    elif schema_type == 'string':
        enum_values = schema.get('enum')
        if enum_values:
            return random.choice(enum_values)
        else:
            min_length = schema.get('minLength', 5)
            max_length = schema.get('maxLength', 15)
            length = random.randint(min_length, max_length)
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


    elif schema_type == 'number':
        minimum = schema.get('minimum', 0)
        maximum = schema.get('maximum', 100)
        return random.uniform(minimum, maximum)

    elif schema_type == 'integer':
        minimum = schema.get('minimum', 0)
        maximum = schema.get('maximum', 100)
        return random.randint(minimum, maximum)

    elif schema_type == 'boolean':
        #return random.choice([True, False])
        return "False"

    elif schema_type == 'null':
        return None

    else:
        # Default case for any unhandled types
        return None

def process_stacks(data):
    stacks = [stack,
              entity_stack({}),
              workflow_stack({}),
              scheduler_stack({}),
              form_submission_stack({}),
              file_upload_stack({}),
              api_request_stack({}),
              data_ingestion_stack({})]
    for single_stack in stacks:
        for item in single_stack:
            if item.get('prompt') and item.get('prompt').get('schema'):
                prompt_text = item['prompt']['text']
                mock_data = generate_data_from_schema(item['prompt']['schema'])
                data[prompt_text[:15]] = mock_data
            elif item.get('function') and item.get('function').get('prompt'):
                prompt_text = item['function']['prompt']['text']
                mock_data = generate_data_from_schema(item['function']['prompt']['schema'])
                data[prompt_text[:15]] = mock_data

# Example usage
def generate_mock_data():
    data = {}
    process_stacks(data)
    print("Generated code snippets have been written to 'generated_chat.py'.")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the file path
    mock_external_data_path = os.path.join(current_dir, "mock_external_data.json")
    with open(mock_external_data_path, 'w') as file:
        file.write(json.dumps(data))

