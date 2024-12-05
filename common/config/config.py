import base64
import os
import logging
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# Load cyoda environment variables
CYODA_AI_URL = os.getenv("CYODA_AI_URL")
API_URL = os.getenv("CYODA_API_URL") + "/api"
decoded_bytes_cyoda_api_key = base64.b64decode(os.getenv("CYODA_API_KEY"))
API_KEY = decoded_bytes_cyoda_api_key.decode("utf-8")
decoded_bytes_cyoda_api_secret = base64.b64decode(os.getenv("CYODA_API_SECRET"))
API_SECRET = decoded_bytes_cyoda_api_secret.decode("utf-8")

ENTITY_VERSION = os.getenv("ENTITY_VERSION", "1000")
GRPC_ADDRESS = os.environ["GRPC_ADDRESS"]
GRPC_PROCESSOR_TAG=os.getenv("GRPC_PROCESSOR_TAG", "elt")

# Load ai assistant environment variables
CLONE_REPO = os.environ["CLONE_REPO"]
MOCK_AI = os.environ["MOCK_AI"]
PROJECT_DIR = os.environ["PROJECT_DIR"]
INSTRUCTION_URL = os.environ["INSTRUCTION_URL"]
REPOSITORY_URL = os.environ["REPOSITORY_URL"]
CYODA_AI_API = os.environ["CYODA_AI_API"]
WORKFLOW_AI_API = os.environ["WORKFLOW_AI_API"]
VALIDATION_MAX_RETRIES = int(os.environ["VALIDATION_MAX_RETRIES"])
MAX_ITERATION = int(os.environ["MAX_ITERATION"])
NUM_MOCK_ARR_ITEMS = int(os.environ["NUM_MOCK_ARR_ITEMS"])
REPOSITORY_NAME = REPOSITORY_URL.split('/')[-1].replace('.git', '')