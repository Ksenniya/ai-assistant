import base64
import os
import logging
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# Load cyoda environment variables
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
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
CLONE_REPO = os.getenv("CLONE_REPO")
MOCK_AI = os.getenv("MOCK_AI")
PROJECT_DIR = os.getenv("PROJECT_DIR")
REPOSITORY_URL = os.getenv("REPOSITORY_URL")
CYODA_AI_API = os.getenv("CYODA_AI_API")
WORKFLOW_AI_API = os.getenv("WORKFLOW_AI_API")
CONNECTION_AI_API = os.getenv("CONNECTION_AI_API")
RANDOM_AI_API = os.getenv("RANDOM_AI_API")
VALIDATION_MAX_RETRIES = int(os.getenv("VALIDATION_MAX_RETRIES"))
MAX_ITERATION = int(os.getenv("MAX_ITERATION"))
NUM_MOCK_ARR_ITEMS = int(os.getenv("NUM_MOCK_ARR_ITEMS"))
REPOSITORY_NAME = os.getenv("REPOSITORY_URL").split('/')[-1].replace('.git', '')
CHAT_REPOSITORY = os.getenv("CHAT_REPOSITORY", "local")
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
MAX_TEXT_SIZE = 50 * 1024 #limit text size to 50KB
MAX_FILE_SIZE = 500 * 1024 #limit file size to 500KB
USER_FILES_DIR_NAME = "entity/user_files"
