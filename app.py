import asyncio
import copy
import functools
import logging
from datetime import timedelta

import jwt

from quart import Quart, request, jsonify, send_from_directory, websocket
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
from common.config.config import MOCK_AI, CYODA_AI_API, ENTITY_VERSION, API_PREFIX, API_URL, ENABLE_AUTH, MAX_TEXT_SIZE, \
    MAX_FILE_SIZE, USER_FILES_DIR_NAME
from common.exception.exceptions import ChatNotFoundException, UnauthorizedAccessException
from common.util.utils import clean_formatting, send_get_request, read_file, \
    get_project_file_name, current_timestamp
from entity.chat.data.data import app_building_stack, APP_BUILDER_FLOW, DESIGN_PLEASE_WAIT, \
    APPROVE_WARNING, DESIGN_IN_PROGRESS_WARNING, OPERATION_NOT_SUPPORTED_WARNING, ADDITIONAL_QUESTION_ROLLBACK_WARNING
from entity.chat.workflow.helper_functions import git_pull, _save_file
from logic.logic import process_dialogue_script
from logic.init import ai_service, cyoda_token, entity_service, chat_lock

PUSH_NOTIFICATION = "push_notification"
APPROVE = "approved"

logger = logging.getLogger('django')

app = Quart(__name__, static_folder='static', static_url_path='')
app = cors(app, allow_origin="*")
rate_limiter = RateLimiter(app)

@app.before_serving
async def add_cors_headers():
    @app.after_request
    async def apply_cors(response):
        # Set CORS headers for all HTTP requests
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow all origins
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'  # Allow these methods
        response.headers['Access-Control-Allow-Headers'] = '*'  # Allow these headers
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # Allow credentials
        return response


@app.errorhandler(UnauthorizedAccessException)
async def handle_unauthorized_exception(error):
    return jsonify({"error": str(error)}), 401


@app.errorhandler(ChatNotFoundException)
async def handle_chat_not_found_exception(error):
    return jsonify({"error": str(error)}), 404


@app.errorhandler(Exception)
async def handle_any_exception(error):
    logger.exception(error)
    return jsonify({"error": str(error)}), 500


# Decorator to enforce authorization
def auth_required(func):
    @functools.wraps(func)  # This ensures the original function's name and metadata are preserved
    async def wrapper(*args, **kwargs):

        if ENABLE_AUTH:
            # Check for Authorization header
            auth_header = websocket.headers.get('Authorization') if websocket else request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "Missing Authorization header"}), 401

            token = auth_header.split(" ")[1]

            # Call external service to validate the token
            response = await send_get_request(token, API_URL, "v1")
            # todo
            if not response or (response.get("status") and response.get("status") == 401):
                raise UnauthorizedAccessException("Invalid token")

        # If the token is valid, proceed to the requested route
        return await func(*args, **kwargs)

    return wrapper

def _get_user_token(auth_header):
    if not auth_header:
        return None
    token = auth_header.split(" ")[1]
    return token

@app.route('/')
@rate_limit(30, timedelta(minutes=1))
async def index():
    # Ensure that 'index.html' is located in the 'static' folder
    return await send_from_directory(app.static_folder, 'index.html')


@app.route(API_PREFIX + '/chat-flow', methods=['GET'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def get_chat_flow():
    return jsonify(APP_BUILDER_FLOW)


@app.route(API_PREFIX + '/chats', methods=['GET'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def get_chats():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    chats = await entity_service.get_items_by_condition(token=auth_header,
                                                        entity_model="chat",
                                                        entity_version=ENTITY_VERSION,
                                                        condition={"cyoda": {
                                                            "operator": "AND",
                                                            "conditions": [
                                                                {
                                                                    "jsonPath": "$.user_id",
                                                                    "operatorType": "EQUALS",
                                                                    "value": user_id,
                                                                    "type": "simple"
                                                                }
                                                            ],
                                                            "type": "group"
                                                        },
                                                            "local": {"key": "user_id", "value": user_id}})
    chats_view = [{
        'technical_id': chat['technical_id'],
        'chat_id': chat['chat_id'],
        'name': chat['name'],
        'description': chat['description'],
        'date': chat['date']
    } for chat in chats]

    return jsonify({"chats": chats_view})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['GET'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def get_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    dialogue = []
    if "finished_flow" in chat.get("chat_flow", {}):
        for item in chat["chat_flow"]["finished_flow"]:
            if item.get("question") or item.get("notification") or item.get("answer"):
                dialogue.append(item)
    chats_view = {
        'technical_id': technical_id,
        'chat_id': chat['chat_id'],
        'name': chat['name'],
        'description': chat['description'],
        'date': chat['date'],
        'dialogue': dialogue
    }
    return jsonify({"chat_body": chats_view})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['DELETE'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def delete_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    await _get_chat_for_user(auth_header, technical_id)
    entity_service.delete_item(token=auth_header,
                               entity_model="chat",
                               entity_version=ENTITY_VERSION,
                               technical_id=technical_id,
                               meta={})

    return jsonify({"message": "Chat deleted", "technical_id": technical_id})


@app.route(API_PREFIX + '/chats', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def add_chat():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    req_data = await request.get_json()
    name = req_data.get('name')
    description = req_data.get('description')
    if not name:
        return jsonify({"message": "Invalid chat name"}), 400
    # Here, handle the answer (e.g., store it, process it, etc.)
    # todo use tech id as chat id

    # new_questions = []
    # questions_stack = copy.deepcopy(new_questions_stack)
    # while questions_stack:
    #     new_questions.append(questions_stack.pop())
    chat = {
        "user_id": user_id,
        "date": current_timestamp(),
        "questions_queue": {"new_questions": [], "asked_questions": []},
        "chat_flow": {"current_flow": copy.deepcopy(app_building_stack), "finished_flow": []},
        "name": name,
        "description": description
    }
    technical_id = await entity_service.add_item(token=auth_header,
                                                 entity_model="chat",
                                                 entity_version=ENTITY_VERSION,
                                                 entity=chat)
    chat = await _get_chat_for_user(auth_header, technical_id)
    chat["chat_id"] = technical_id
    await entity_service.update_item(token=auth_header,
                                     entity_model="chat",
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=chat,
                                     meta={})
    logger.info("chat_id=" + str(chat["chat_id"]))
    asyncio.create_task(process_dialogue_script(auth_header, technical_id))
    return jsonify({"message": "Chat created", "technical_id": technical_id}), 200


# polling for new questions here
@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['GET'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def get_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    questions_queue = chat.get("questions_queue", {}).get("new_questions", [])
    return await poll_questions(auth_header, chat, questions_queue, technical_id)


@app.route(API_PREFIX + '/chats/<technical_id>/notification', methods=['PUT'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def edit_file(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    req_data = await request.get_json()
    # todo
    data = req_data.get('notification')
    if data and len(str(data).encode('utf-8')) > MAX_TEXT_SIZE:
        return jsonify({"error": "Answer size exceeds 1MB limit"}), 400
    await _save_file(chat_id=chat["chat_id"], _data=data, item=req_data.get('file_name'))
    finished_flow = chat["chat_flow"].get("finished_flow", [])
    for i in range(len(finished_flow) - 1, -1, -1):  # Start from the end
        if finished_flow[i].get("file_name") and finished_flow[i].get("file_name") == req_data.get('file_name'):
            # Insert a new element after the found element
            req_data["answer"] = data
            req_data["notification"] = None
            finished_flow.insert(i + 1, req_data)
            break
    await entity_service.update_item(token=auth_header,
                                     entity_model="chat",
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=chat,
                                     meta={})
    return jsonify({"questions": []}), 200


@app.route(API_PREFIX + '/chats/<technical_id>/text-questions', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def submit_question_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)

    req_data = await request.get_json()
    question = req_data.get('question')
    res = await _submit_question_helper(auth_header, chat, question)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def submit_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)

    req_data = await request.form
    req_data = req_data.to_dict()
    question = req_data.get('question')
    file = await request.files
    user_file = file.get('file')
    if user_file.content_length > MAX_FILE_SIZE:
        return {"error": f"File size exceeds {MAX_FILE_SIZE} limit"}
    res = await _submit_question_helper(chat, question, user_file)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/push-notify', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def push_notify(technical_id):
    return jsonify({"error": OPERATION_NOT_SUPPORTED_WARNING}), 400
    # auth_header = request.headers.get('Authorization')
    # chat = await _get_chat_for_user(auth_header, technical_id)
    # await git_pull(chat['chat_id'])
    # return await _submit_answer_helper(technical_id, PUSH_NOTIFICATION, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/approve', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def approve(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    return await _submit_answer_helper(technical_id, APPROVE, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/rollback', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def rollback(technical_id):
    auth_header = request.headers.get('Authorization')
    req_data = await request.get_json()
    if not req_data.get('question') or not req_data.get('stack'):
        return jsonify({"error": ADDITIONAL_QUESTION_ROLLBACK_WARNING}), 400
    question = req_data.get('question') if req_data else None
    chat = await _get_chat_for_user(auth_header, technical_id)
    return await rollback_dialogue_script(technical_id, auth_header, chat, question)


@app.route(API_PREFIX + '/chats/<technical_id>/text-answers', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def submit_answer_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    req_data = await request.get_json()
    answer = req_data.get('answer')
    if answer and len(str(answer).encode('utf-8')) > MAX_TEXT_SIZE:
        return jsonify({"error": "Answer size exceeds 1MB limit"}), 400
    return await _submit_answer_helper(technical_id, answer, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/answers', methods=['POST'])
@auth_required
@rate_limit(30, timedelta(minutes=1))
async def submit_answer(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    req_data = await request.form
    req_data = req_data.to_dict()
    answer = req_data.get('answer')

    # Check if a file has been uploaded
    file = await request.files
    user_file = file.get('file')
    if user_file.content_length > MAX_FILE_SIZE:
        return {"error": f"File size exceeds {MAX_FILE_SIZE} limit"}
    return await _submit_answer_helper(technical_id, answer, auth_header, chat, user_file)


def _get_user_id(auth_header):
    try:
        if not auth_header and ENABLE_AUTH:
            return jsonify({"error": "Invalid token"}), 401
        if not ENABLE_AUTH:
            user_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            return f'User IP: {user_ip}, User-Agent: {user_agent}'
        token = auth_header.split(" ")[1]
        # Decode the JWT without verifying the signature
        # The `verify=False` option ensures that we do not verify the signature
        # This is useful for extracting the payload only.
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")  # todo change to userId when ready
        return user_id
    except jwt.InvalidTokenError:
        return None


async def _get_chat_for_user(auth_header, technical_id):
    user_id = _get_user_id(auth_header)
    if not user_id:
        raise UnauthorizedAccessException()

    chat = await entity_service.get_item(token=auth_header,
                                         entity_model="chat",
                                         entity_version=ENTITY_VERSION,
                                         technical_id=technical_id)

    if not chat:
        raise ChatNotFoundException()

    if chat["user_id"] != user_id:
        raise UnauthorizedAccessException()

    return chat


async def _submit_question_helper(auth_header, chat, question, user_file=None):
    # Check if a file has been uploaded

    # Validate input
    if not question:
        return jsonify({"message": "Invalid entity"}), 400

    # Return mock response if AI mock mode is enabled
    if MOCK_AI == "true":
        return jsonify({"message": "mock ai answer"}), 200

    # Process file if provided
    if user_file:
        file_name = user_file.filename
        folder_name = USER_FILES_DIR_NAME
        # Save the uploaded file asynchronously
        await _save_file(chat_id=chat["chat_id"], _data=user_file, item=file_name, folder_name=folder_name)
        # Call AI service with the file
        result = await ai_service.ai_chat(
            token=auth_header,
            chat_id=chat["chat_id"],
            ai_endpoint=CYODA_AI_API,
            ai_question=question,
            user_file=file_name
        )
    else:
        # Call AI service without a file
        result = await ai_service.ai_chat(
            token=auth_header,
            chat_id=chat["chat_id"],
            ai_endpoint=CYODA_AI_API,
            ai_question=question
        )

    # Return the result from the AI service
    return jsonify({"message": result}), 200


async def rollback_dialogue_script(technical_id, auth_header, chat, question):
    current_flow = chat["chat_flow"]["current_flow"]
    if "finished_flow" not in chat["chat_flow"]:
        chat["chat_flow"]["finished_flow"] = []
    finished_flow = chat["chat_flow"]["finished_flow"]
    if not finished_flow[-1].get("question"):
        return jsonify({
            "message": DESIGN_IN_PROGRESS_WARNING}), 400
    if not question:
            return jsonify({
                "message": OPERATION_NOT_SUPPORTED_WARNING}), 400
    event = finished_flow.pop()
    while finished_flow and (not event.get("question") or event.get("question") != question):
        if event.get("stack") and (not event.get('iteration') or (event.get('iteration') and event.get('iteration') < 2)):
            new_event=copy.deepcopy(event)
            new_event['iteration']=0
            current_flow.append(new_event)
        event = finished_flow.pop()
    finished_flow.append(event)
    await entity_service.update_item(token=auth_header,
                                     entity_model="chat",
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=chat,
                                     meta={})
    return jsonify({"message": "Answer received"}), 200


async def _submit_answer_helper(technical_id, answer, auth_header, chat, user_file=None):
    if "questions_queue" not in chat:
        chat["questions_queue"] = {}
    if "new_questions" not in chat["questions_queue"]:
        chat["questions_queue"]["new_questions"] = []
    question_queue = chat["questions_queue"]["new_questions"]
    if len(question_queue) > 0:
        return jsonify({
            "message": "Could you please have a look at a couple of more questions before submitting your answer?"}), 400
    if not answer:
        return jsonify({"message": "Invalid entity"}), 400

    wait_notification = {"notification": DESIGN_PLEASE_WAIT,
                         "prompt": {},
                         "answer": None,
                         "function": None,
                         "iteration": 0,
                         "max_iteration": 0
                         }
    question_queue.append(wait_notification)

    async with chat_lock:
        current_stack = chat["chat_flow"]["current_flow"]
        finished_stack = chat["chat_flow"].get("finished_flow", [])
        if not current_stack:
            return jsonify({"message": "Finished"}), 200
        #question_queue.append(wait_notification)
        if not finished_stack[-1].get("question"):
            retry_notification = {"notification": DESIGN_IN_PROGRESS_WARNING}
            question_queue.append(retry_notification)
            return jsonify({
                "message": DESIGN_IN_PROGRESS_WARNING}), 400
        if answer == APPROVE and finished_stack[-1].get("question") and not finished_stack[-1].get("approve"):
            retry_notification = {"notification": APPROVE_WARNING}
            question_queue.append(retry_notification)
            return jsonify({
                "message": APPROVE_WARNING}), 400
        next_event = current_stack[-1]
        while next_event.get("notification"):
            next_event_notification = current_stack.pop()
            question_queue.append(next_event_notification)
            next_event = current_stack[-1]
        # if answer == PUSH_NOTIFICATION:
        #     next_event["answer"] = clean_formatting(
        #         await read_file(get_project_file_name(chat['chat_id'], next_event["file_name"])))
        if answer == APPROVE:
            next_event["max_iteration"] = -1
            next_event["answer"] = APPROVE
        else:
            next_event["answer"] = clean_formatting(answer)
    if user_file:
        file_name = user_file.filename
        folder_name = USER_FILES_DIR_NAME
        await _save_file(chat_id=chat["chat_id"], _data=user_file, item=file_name, folder_name=folder_name)
        next_event["user_file"] = file_name
        next_event["user_file_processed"] = False
    await entity_service.update_item(token=auth_header,
                                     entity_model="chat",
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=chat,
                                     meta={})
    asyncio.create_task(process_dialogue_script(auth_header, technical_id))
    return jsonify({"message": "Answer received"}), 200


async def poll_questions(auth_header, chat, questions_queue, technical_id):
    try:
        questions_to_user = []
        while questions_queue:
            _event = questions_queue.pop(0)
            questions_to_user.append(_event)
        if len(questions_to_user) > 0:
            await entity_service.update_item(token=auth_header,
                                             entity_model="chat",
                                             entity_version=ENTITY_VERSION,
                                             technical_id=technical_id,
                                             entity=chat,
                                             meta={})
        return jsonify({"questions": questions_to_user}), 200
    except Exception as e:
        logger.exception(e)
        return jsonify({"questions": []}), 200  # No Content


if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=5000, threaded=True)
