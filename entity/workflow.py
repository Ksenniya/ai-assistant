import glob
import importlib
import inspect
import logging
import os

import entity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
process_dispatch = {}

def find_and_import_workflows():
    entity_path = entity.__path__[0]
    # Pattern to match 'entity/*/workflow/workflow.py'
    pattern = os.path.join(entity_path, '*', 'workflow', 'workflow.py')
    for module_path in glob.glob(pattern):
        # Compute the module name
        # Example: if module_path is '/path/to/entity/any_name/workflow/workflow.py'
        # The module name should be 'entity.any_name.workflow.workflow'
        relative_path = os.path.relpath(module_path, entity_path)
        module_name = entity.__name__ + '.' + relative_path.replace(os.sep, '.')[:-3]  # Remove '.py' extension
        try:
            # Import the module from the file path
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Collect all functions that don't start with an underscore
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if not name.startswith("_"):
                        process_dispatch[name] = func
        except Exception as e:
            print(f"Error importing module {module_name}: {e}")

# Run the function to populate process_dispatch
find_and_import_workflows()

async def dispatch_function(token, event, chat):
    if event["function"]["name"] in process_dispatch:
        response = await process_dispatch[event["function"]["name"]](token, event, chat)
    else:
        raise ValueError(f"Unknown processing step: {event["function"]["name"]}")
    return response

async def process_event(token, data, processor_name):
    meta = {"token": token, "entity_model": "ENTITY_PROCESSED_NAME", "entity_version": "ENTITY_VERSION"}
    payload_data = data['payload']['data']
    if processor_name in process_dispatch:
        try:
            response = await process_dispatch[processor_name](meta, payload_data)
        except Exception as e:
            logger.info(f"Error processing event: {e}")
            raise
    else:
        raise ValueError(f"Unknown processing step: {processor_name}")
    return response
