from pathlib import Path

from common.config.config import ENTITY_VERSION
from common.repository.cyoda.cyoda_repository import CyodaRepository

cyoda_repository = CyodaRepository()

def init_cyoda(token):
    entity_dir = Path(__file__).resolve().parent.parent.parent.parent / 'entity'

    for json_file in entity_dir.glob('*/**/*.json'):
    # Ensure the JSON file is in an immediate subdirectory
        if json_file.parent.parent.name != entity_dir.name or json_file.parent.name != json_file.name.replace(".json", ""):
            continue

        try:
            with open(json_file, 'r') as file:
                entity = file.read()
                entity_name = json_file.name.replace(".json", "")
                if not cyoda_repository._model_exists(token, entity_name, ENTITY_VERSION):
                    cyoda_repository._save_entity_schema(token, entity_name, ENTITY_VERSION, entity)
                    cyoda_repository._lock_entity_schema(token, entity_name, ENTITY_VERSION, None)
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
