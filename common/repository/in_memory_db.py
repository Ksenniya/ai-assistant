import threading
from typing import List, Any

from common.repository.crud_repository import CrudRepository
from common.util.utils import *

logger = logging.getLogger('django')

cache = {}


class InMemoryRepository(CrudRepository):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        logger.info("initializing CyodaService")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(InMemoryRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_meta(self, token, entity_model, entity_version):
        return {"token": token, "entity_model": entity_model, "entity_version": entity_version}

    def count(self, meta) -> int:
        pass

    def delete_all(self, meta) -> None:
        pass

    def delete_all_entities(self, meta, entities: List[Any]) -> None:
        pass

    def delete_all_by_key(self, meta, keys: List[Any]) -> None:
        pass

    def delete_by_key(self, meta, key: Any) -> None:
        pass

    def exists_by_key(self, meta, key: Any) -> bool:
        pass

    def find_all(self, meta) -> List[Any]:
        pass

    def find_all_by_key(self, meta, keys: List[Any]) -> List[Any]:
        pass

    def find_by_key(self, meta, key: Any) -> Optional[Any]:
        pass

    def find_by_id(self, meta, uuid: Any) -> Optional[Any]:
        return cache.get(uuid)

    def find_all_by_criteria(self, meta, criteria: Any) -> Optional[Any]:
        entities = []
        for uuid in cache:
            if cache[uuid][criteria["key"]] == criteria["value"]:
                cache[uuid]['technical_id'] = uuid
                entities.append(cache[uuid])
        return entities

    def save(self, meta, entity: Any) -> Any:
        uuid = str(generate_uuid())
        cache[uuid] = entity
        return uuid

    def save_all(self, meta, entities: List[Any]) -> bool:
        pass

    def update(self, meta, id, entity: Any) -> Any:
        cache[id] = entity

    def update_all(self, meta, entities: List[Any]) -> List[Any]:
        pass

    def delete(self, meta, entity: Any) -> None:
        pass

    def delete_by_id(self, meta, technical_id: Any) -> None:
        del cache[technical_id]
