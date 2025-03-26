import base64
import os
import logging
from dotenv import load_dotenv

from common.config.conts import DEPLOY_CYODA_ENV, DEPLOY_USER_APP, DEPLOY_STATUS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
get_env = lambda key: os.getenv(key) or (_ for _ in ()).throw(Exception(f"{key} not found"))

CYODA_HOST = get_env("CYODA_HOST")
CYODA_AI_URL = os.getenv("CYODA_AI_URL", f"https://{CYODA_HOST}/ai")
CYODA_API_URL = os.getenv("CYODA_API_URL", f"https://{CYODA_HOST}/api")
GRPC_ADDRESS = os.getenv("GRPC_ADDRESS", f"grpc-{CYODA_HOST}")
# Load cyoda environment variables
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
DEEPSEEK_API_KEY = get_env("DEEPSEEK_API_KEY")
API_URL = os.getenv("CYODA_API_URL") + "/api"
decoded_bytes_cyoda_api_key = base64.b64decode(os.getenv("CYODA_API_KEY"))
API_KEY = decoded_bytes_cyoda_api_key.decode("utf-8")
decoded_bytes_cyoda_api_secret = base64.b64decode(os.getenv("CYODA_API_SECRET"))
API_SECRET = decoded_bytes_cyoda_api_secret.decode("utf-8")

ENTITY_VERSION = os.getenv("ENTITY_VERSION", "1000")
GRPC_PROCESSOR_TAG = os.getenv("GRPC_PROCESSOR_TAG", "elt")

# Load ai assistant environment variables
CLONE_REPO = get_env("CLONE_REPO")
MOCK_AI = get_env("MOCK_AI")
PROJECT_DIR = get_env("PROJECT_DIR")
REPOSITORY_URL = get_env("REPOSITORY_URL")
CYODA_AI_API = get_env("CYODA_AI_API")
WORKFLOW_AI_API = get_env("WORKFLOW_AI_API")
CONNECTION_AI_API = get_env("CONNECTION_AI_API")
RANDOM_AI_API = get_env("RANDOM_AI_API")
VALIDATION_MAX_RETRIES = int(get_env("VALIDATION_MAX_RETRIES"))
MAX_ITERATION = int(os.getenv("MAX_ITERATION", 30))
MAX_AI_AGENT_ITERATIONS = int(os.getenv("MAX_AI_AGENT_ITERATIONS", 20))
MAX_GUEST_CHATS = int(os.getenv("MAX_GUEST_CHATS", 2))
CHECK_DEPLOY_INTERVAL = int(os.getenv("CHECK_DEPLOY_INTERVAL", 60))
NUM_MOCK_ARR_ITEMS = int(get_env("NUM_MOCK_ARR_ITEMS"))
REPOSITORY_NAME = get_env("REPOSITORY_URL").split('/')[-1].replace('.git', '')
CHAT_REPOSITORY = os.getenv("CHAT_REPOSITORY", "local")
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
MAX_TEXT_SIZE = 50 * 1024  # limit text size to 50KB
MAX_FILE_SIZE = 500 * 1024  # limit file size to 500KB
USER_FILES_DIR_NAME = "entity/user_files"
RAW_REPOSITORY_URL = get_env("RAW_REPOSITORY_URL")
GOOGLE_SEARCH_KEY = get_env("GOOGLE_SEARCH_KEY")
GOOGLE_SEARCH_CX = get_env("GOOGLE_SEARCH_CX")
AUTH_SECRET_KEY = get_env("AUTH_SECRET_KEY")
CYODA_DEPLOY_DICT = {
    DEPLOY_CYODA_ENV: os.getenv("DEPLOY_CYODA_ENV", f"https://infra-{CYODA_HOST}/deploy/cyoda-env"),
    DEPLOY_USER_APP: os.getenv("DEPLOY_USER_APP", f"https://infra-{CYODA_HOST}/deploy/user_app"),
    DEPLOY_STATUS: os.getenv("DEPLOY_STATUS", f"https://infra-{CYODA_HOST}/deploy/cyoda-env/status")
}
MAX_IPS_PER_DEVICE_BEFORE_BLOCK=int(os.getenv("MAX_IPS_PER_DEVICE_BEFORE_BLOCK", 300))
MAX_IPS_PER_DEVICE_BEFORE_ALARM=int(os.getenv("MAX_IPS_PER_DEVICE_BEFORE_ALARM", 100))
MAX_SESSIONS_PER_IP=int(os.getenv("MAX_SESSIONS_PER_IP", 100))