import logging
from abc import ABC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
process_dispatch = {}

class Workflow(ABC):
    pass

