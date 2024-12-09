import logging
import threading
from typing import Any, List

from common.repository.crud_repository import CrudRepository
from common.service.entity_service_interface import EntityService

logger = logging.getLogger('django')

class EntityServiceImpl(EntityService):
    _instance = None
    _lock = threading.Lock()
    _repository: CrudRepository = None

    def __new__(cls, repository: CrudRepository = None):
        logger.info("initializing CyodaService")
        # Ensuring only one instance is created
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EntityServiceImpl, cls).__new__(cls)
                    # Only initialize _repository during the first instantiation
                    if repository is not None:
                        cls._instance._repository = repository
        return cls._instance

    def __init__(self, repository: CrudRepository):
        # You can leave this empty if no further initialization is required,
        # or add additional initialization logic here if needed.
        pass

    def get_item(self, token: str, entity_model: str, entity_version: str, technical_id: str) -> Any:
        """Retrieve a single item based on its ID."""
        meta = self._repository.get_meta(token, entity_model, entity_version)
        resp = self._repository.find_by_id(meta, technical_id)
        return resp

    def get_items(self, token: str, entity_model: str, entity_version: str) -> List[Any]:
        """Retrieve multiple items based on their IDs."""
        meta = self._repository.get_meta(token, entity_model, entity_version)
        resp = self._repository.find_all(meta)
        return resp

    def get_single_item_by_condition(self, token: str, entity_model: str, entity_version: str, condition: Any) -> List[Any]:
        """Retrieve multiple items based on their IDs."""
        resp = self._find_by_criteria(token, entity_model, entity_version, condition)
        return resp[0]

    def get_items_by_condition(self, token: str, entity_model: str, entity_version: str, condition: Any) -> List[Any]:
        """Retrieve multiple items based on their IDs."""
        resp = self._find_by_criteria(token, entity_model, entity_version, condition)
        return resp

    def add_item(self, token: str, entity_model: str, entity_version: str, entity: Any) -> Any:
        """Add a new item to the repository."""
        meta = self._repository.get_meta(token, entity_model, entity_version)
        resp = self._repository.save(meta, entity)
        return resp

    def update_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, entity: Any, meta: Any) -> Any:
        """Update an existing item in the repository."""
        meta = meta.update(self._repository.get_meta(token, entity_model, entity_version))
        resp = self._repository.update(meta, technical_id, entity)
        return resp

    def _find_by_criteria(self, token, entity_model, entity_version, condition):
        meta = self._repository.get_meta(token, entity_model, entity_version)
        resp = self._repository.find_all_by_criteria(meta, condition)
        return resp

    def delete_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, meta: Any) -> Any:
        """Update an existing item in the repository."""
        meta = meta.update(self._repository.get_meta(token, entity_model, entity_version))
        resp = self._repository.delete_by_id(meta, technical_id)
        return resp