import os
import logging
import subprocess
import time
import re
import requests
from typing import Optional
import uuid
import json
import jsonschema
from jsonschema import validate

from common.config.config import PROJECT_DIR, REPOSITORY_NAME

logger = logging.getLogger(__name__)


def get_user_history_answer(response):
    answer = response.get('message', '') if response and isinstance(response, dict) else ''
    if isinstance(answer, dict) or isinstance(answer, list):
        answer = json.dumps(answer)
    return answer


def generate_uuid() -> uuid:
    return uuid.uuid1()


def _normalize_boolean_json(json_data):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, str):
                if (value in ["'true'", "'True'", 'True', "true", "True"]):
                    json_data[key] = True
                elif (value in ["'false'", "'False'", 'False', "false", "False"]):
                    json_data[key] = False
            elif isinstance(value, dict):
                json_data[key] = _normalize_boolean_json(value)
    return json_data


def parse_json(result: str) -> str:
    if isinstance(result, dict):
        return json.dumps(result)
    if result.startswith("```"):
        return "\n".join(result.split("\n")[1:-1])
    if not result.startswith("{"):
        start_index = result.find("```json")
        if start_index != -1:
            start_index += len("```json\n")
            end_index = result.find("```", start_index)
            return result[start_index:end_index].strip()
    return result


def parse_workflow_json(result: str) -> str:
    # Function to replace single quotes with double quotes and handle True/False
    def convert_to_json_compliant_string(text: str) -> str:
        # Convert Python-style booleans to JSON booleans (True -> true, False -> false)
        text = text.replace("True", "true").replace("False", "false")

        # Replace single quotes with double quotes for strings
        # This replacement will happen only for string-like values (inside curly braces or key-value pairs)
        text = re.sub(r"(?<=:)\s*'(.*?)'\s*(?=\s*,|\s*\})", r'"\1"', text)  # For values
        text = re.sub(r"(?<=,|\{|\[)\s*'(.*?)'\s*(?=\s*:|\s*,|\s*\])", r'"\1"', text)  # For keys

        # Ensure the surrounding quotes around strings
        text = re.sub(r"(?<=:)\s*'(.*?)'\s*(?=\s*,|\s*\})", r'"\1"', text)
        return text

    # If result is a dictionary, convert it to JSON with double quotes
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)

    # If result is a string, process it for improper quote handling
    if isinstance(result, str):
        if result.startswith("```json"):
            # Extract the content inside the json code block
            start_index = result.find("```json") + len("```json\n")
            end_index = result.find("```", start_index)
            json_content = result[start_index:end_index].strip()

            # Apply the corrections: Convert single quotes, True/False to JSON-compatible format
            json_content = convert_to_json_compliant_string(json_content)

            # Try to parse the extracted content as JSON
            try:
                parsed_json = json.loads(json_content)
                return json.dumps(parsed_json, ensure_ascii=False)
            except json.JSONDecodeError:
                return json_content  # If parsing fails, return the original content as is
        elif result.startswith("```"):
            # If result is a general code block, strip the backticks and return it
            return "\n".join(result.split("\n")[1:-1])
        else:
            # Apply the corrections to the string content
            result = convert_to_json_compliant_string(result)
            return result

    # Return result as-is if it's neither a dictionary nor a valid string format
    return result

# def validate_result(parsed_result: str, file_path: str, schema: Optional[str]) -> str:
#     if file_path:
#         try:
#             with open(file_path, "r") as schema_file:
#                 schema = json.load(schema_file)
#         except (FileNotFoundError, json.JSONDecodeError) as e:
#             logger.error(f"Error reading schema file {file_path}: {e}")
#             raise
#
#     try:
#         json_data = json.loads(parsed_result)
#         normalized_json_data = _normalize_boolean_json(json_data)
#         validate(instance=normalized_json_data, schema=schema)
#         logger.info("JSON validation successful.")
#         return normalized_json_data
#     except jsonschema.exceptions.ValidationError as err:
#         logger.error(f"JSON validation failed: {err.message}")
#         raise
#     except json.JSONDecodeError as e:
#         logger.error(f"Failed to decode JSON: {e}")
#         raise


def validate_result(parsed_result: str, file_path: str) -> bool:
    try:
        with open(file_path, "r") as schema_file:
            schema = json.load(schema_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error reading schema file {file_path}: {e}")
        raise

    try:
        json_data = json.loads(parsed_result)
        validator = jsonschema.Draft7Validator(schema)
        errors = sorted(validator.iter_errors(json_data), key=lambda e: e.path)

        if errors:
            error_messages = []
            for error in errors:
                error_messages.append(
                    f"Message: {error.message}\n"
                    f"Schema path: {'.'.join(map(str, error.schema_path))}\n"
                    f"Instance path: {'.'.join(map(str, error.path))}"
                )
            full_error_message = "\n\n".join(error_messages)
            logger.error(f"JSON validation failed:\n{full_error_message}")
            raise jsonschema.exceptions.ValidationError(full_error_message)

        logger.info("JSON validation successful.")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        raise

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        logger.warning(f"Environment variable {name} not found.")
    return value


def read_file(file_path: str):
    """Read and return JSON entity from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to read JSON file {file_path}: {e}")
        raise


def read_json_file(file_path: str):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        logger.info(f"Successfully read JSON file: {file_path}")
        return data
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed for file {file_path}: {e}")
        raise


def send_get_request(token: str, api_url: str, path: str) -> Optional[requests.Response]:
    url = f"{api_url}/{path}"
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = requests.get(url, headers=headers)
        # Raise an error for bad status codes
        logger.info(f"GET request to {url} successful.")
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during GET request to {url}: {http_err}")
        raise
    except Exception as err:
        logger.error(f"Error during GET request to {url}: {err}")
        raise


def send_post_request(token: str, api_url: str, path: str, data=None, json=None) -> Optional[requests.Response]:
    url = f"{api_url}/{path}"
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = requests.post(url, headers=headers, data=data, json=json)
        response.raise_for_status()  # Raise an error for bad status codes
        logger.info(f"POST request to {url} successful.")
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during POST request to {url}: {http_err}")
        raise
    except Exception as err:
        logger.error(f"Error during POST request to {url}: {err}")
        raise


def send_put_request(token: str, api_url: str, path: str, data=None, json=None) -> Optional[requests.Response]:
    url = f"{api_url}/{path}"
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = requests.put(url, headers=headers, data=data, json=json)
        response.raise_for_status()  # Raise an error for bad status codes
        logger.info(f"PUT request to {url} successful.")
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during PUT request to {url}: {http_err}")
        raise
    except Exception as err:
        logger.error(f"Error during PUT request to {url}: {err}")
        raise


def send_delete_request(token: str, api_url: str, path: str) -> Optional[requests.Response]:
    url = f"{api_url}/{path}"
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        logger.info(f"GET request to {url} successful.")
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during GET request to {url}: {http_err}")
        raise
    except Exception as err:
        logger.error(f"Error during GET request to {url}: {err}")
        raise


def expiration_date(seconds: int) -> int:
    return int((time.time() + seconds) * 1000.0)


def now():
    timestamp = int(time.time() * 1000.0)
    return timestamp


def timestamp_before(seconds: int) -> int:
    return int((time.time() - seconds) * 1000.0)

def clean_formatting(text):
    """
    Convert multi-line text into a single line, preserving all other content.
    """
    # Replace any sequence of newlines (and carriage returns) with a single space
    return re.sub(r'[\r\n]+', ' ', text)
# def clean_formatting(text):
#     """
#     This function simulates the behavior of text pasted into Google search:
#     - Removes leading and trailing whitespace.
#     - Condenses multiple spaces into a single space.
#     - Keeps alphanumeric characters and spaces only, removing other characters.
#
#     :param answer: The input string to be cleaned
#     :return: A cleaned string
#     """
#     # Remove leading and trailing whitespace
#     text = text.strip()
#
#     # Condense multiple spaces into a single space
#     text = re.sub(r'\s+', ' ', text)
#
#     # Remove non-alphanumeric characters (excluding spaces)
#     text = re.sub(r'[^\w\s]', '', text)
#
#     return text



def git_pull(chat_id):

    clone_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}"
    os.chdir(clone_dir)
    # Create a new branch with the name $chat_id
    subprocess.run(["git", "checkout", str(chat_id)], check=True)
    try:
        # Push the new branch to the remote repository
        subprocess.run(["git", "pull", "origin", str(chat_id)], check=True)
    except Exception as e:
        logger.error(f"Error during git push: {e}")
        logger.exception(e)


def get_project_file_name(chat_id, file_name):
    return f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}/{file_name}"