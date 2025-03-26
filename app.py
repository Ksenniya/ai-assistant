import asyncio
import copy
import datetime
import functools
import json
import logging
import uuid
from datetime import timedelta
import jwt
import aiohttp
import aiofiles

from quart import Quart, request, jsonify, send_from_directory, websocket
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
from common.config.config import MOCK_AI, CYODA_AI_API, ENTITY_VERSION, API_PREFIX, API_URL, ENABLE_AUTH, MAX_TEXT_SIZE, \
    MAX_FILE_SIZE, USER_FILES_DIR_NAME, CHAT_REPOSITORY, RAW_REPOSITORY_URL, MAX_GUEST_CHATS, AUTH_SECRET_KEY, \
    MAX_ITERATION
from common.config.conts import EDITING_AGENT, APP_BUILDER_MODE, OPEN_AI
from common.exception.exceptions import ChatNotFoundException, InvalidTokenException
from common.util.file_reader import read_file_content
from common.util.utils import clean_formatting, send_get_request, current_timestamp, _save_file, clone_repo, \
    validate_token
from entity.chat.data.data import app_building_stack, APP_BUILDER_FLOW, DESIGN_PLEASE_WAIT, \
    APPROVE_WARNING, DESIGN_IN_PROGRESS_WARNING, OPERATION_NOT_SUPPORTED_WARNING, ADDITIONAL_QUESTION_ROLLBACK_WARNING
from logic.init import BeanFactory

PUSH_NOTIFICATION = "push_notification"
APPROVE = "approved, let's proceed to the next iteration immediately"
RATE_LIMIT = 300
logger = logging.getLogger('django')

app = Quart(__name__, static_folder='static', static_url_path='')
app = cors(app, allow_origin="*")
rate_limiter = RateLimiter(app)
factory = BeanFactory(config={"CHAT_REPOSITORY": "cyoda"})
ai_agent = factory.get_services()["ai_agent"]
entity_service = factory.get_services()["entity_service"]
flow_processor = factory.get_services()["flow_processor"]
chat_lock = factory.get_services()["chat_lock"]


async def load_fsm():
    try:
        FILENAME = "/home/kseniia/PycharmProjects/ai_assistant/entity/chat/data/workflow_prototype/agentic_workflow.json"
        async with aiofiles.open(FILENAME, "r") as f:
            data = await f.read()
        fsm = json.loads(data)
        return fsm
    except Exception as e:
        logger.info(f"Error reading JSON file: {e}")
        return None


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


@app.errorhandler(InvalidTokenException)
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
                raise InvalidTokenException("Invalid token")

            user_id = _get_user_id(auth_header=auth_header)
            if user_id.startswith('guest.'):
                return jsonify({"error": "This action is not available. Please sign in to proceed"}), 403

            token = auth_header.split(" ")[1]
            response = await send_get_request(token, API_URL, "v1")
            # todo
            if not response or (response.get("status") and response.get("status") == 401):
                raise InvalidTokenException("Invalid token")

        # If the token is valid, proceed to the requested route
        return await func(*args, **kwargs)

    return wrapper


# Decorator to enforce authorization
def auth_required_to_proceed(func):
    @functools.wraps(func)  # This ensures the original function's name and metadata are preserved
    async def wrapper(*args, **kwargs):

        if ENABLE_AUTH:
            # Check for Authorization header
            auth_header = websocket.headers.get('Authorization') if websocket else request.headers.get('Authorization')
            if not auth_header:
                raise InvalidTokenException("Invalid token")

            user_id = _get_user_id(auth_header=auth_header)
            if user_id.startswith('guest.'):
                chat = await _get_chat_for_user(request=request, auth_header=auth_header,
                                                technical_id=request.view_args.get("technical_id"))
                current_stack = chat["chat_flow"]["current_flow"]
                if not current_stack:
                    return jsonify({"error": "Max iteration reached, please sign in to proceed"}), 403
                next_event = current_stack[-1]
                if not next_event.get("allow_anonymous_users", False):
                    return jsonify({"error": "Max iteration reached, please sign in to proceed"}), 403
            else:
                token = auth_header.split(" ")[1]
                # Call external service to validate the token
                response = await send_get_request(token, API_URL, "v1")
                # todo
                if not response or (response.get("status") and response.get("status") == 401):
                    raise InvalidTokenException("Invalid token")

        # If the token is valid, proceed to the requested route
        return await func(*args, **kwargs)

    return wrapper


def _get_user_token(auth_header):
    if not auth_header:
        return None
    token = auth_header.split(" ")[1]
    return token


@app.route('/')
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def index():
    # Ensure that 'index.html' is located in the 'static' folder
    return await send_from_directory(app.static_folder, 'index.html')


@app.route(API_PREFIX + '/chat-flow', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def get_chat_flow():
    return jsonify(APP_BUILDER_FLOW)


@app.route(API_PREFIX + '/chats', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def get_chats():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header=auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    chats = await _get_chats_by_user_name(auth_header, user_id)
    chats_view = [{
        'technical_id': chat['technical_id'],
        'name': chat['name'],
        'description': chat['description'],
        'date': "2025-01-30T23:48:21.073+00:00"
    } for chat in chats]

    return jsonify({"chats": chats_view})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def get_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)

    dialogue = []
    if "finished_flow" in chat.get("chat_flow", {}):
        for item in chat["chat_flow"]["finished_flow"]:
            if ((item.get("question") or item.get("notification")) and item.get("publish")) or item.get("answer"):
                dialogue.append(item)
    chats_view = {
        'technical_id': technical_id,
        'name': chat['name'],
        'description': chat['description'],
        'date': chat['date'],
        'dialogue': dialogue
    }
    return jsonify({"chat_body": chats_view})


@app.route(API_PREFIX + '/get_guest_token', methods=['GET'])
# todo !!! @rate_limit(limit=3, period=timedelta(days=1))
async def get_guest_token():
    session_id = uuid.uuid4()
    payload = {
        "sub": f"guest.{session_id}",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour
    }

    # Generate the token using HS256 algorithm
    token = jwt.encode(payload, AUTH_SECRET_KEY, algorithm="HS256")
    return jsonify({"access_token": token})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['DELETE'])
# todo !! @auth_required
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def delete_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    entity_service.delete_item(token=auth_header,
                               entity_model="chat",
                               entity_version=ENTITY_VERSION,
                               technical_id=technical_id,
                               meta={})

    return jsonify({"message": "Chat deleted", "technical_id": technical_id})


@app.route(API_PREFIX + '/chats', methods=['POST'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def add_chat():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header=auth_header)
    if user_id.startswith('guest.'):
        user_chats = await _get_chats_by_user_name(auth_header, user_id)
        if len(user_chats) >= MAX_GUEST_CHATS:
            return jsonify({"error": "Max guest chats limit reached, please sign in to proceed"}), 403
    req_data = await request.get_json()
    chat = {
        "user_id": user_id,
        "date": current_timestamp(),
        "questions_queue": {"new_questions": [], "asked_questions": []},
        "name": req_data.get('name'),
        "description": req_data.get('description'),
        "chat_flow": {"current_flow": [], "finished_flow": []},
        "transitions": {
            "conditions": {},
            "current_iteration": {},
            "max_iteration": {}
        },
        "messages": []
    }
    technical_id = await entity_service.add_item(token=auth_header,
                                                 entity_model="chat",
                                                 entity_version=ENTITY_VERSION,
                                                 entity=chat)
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    logger.info("chat_id=" + str(technical_id))
    #####todo SIMULATION!!!

    # --- Simulation 1: Successful Weather Fetch Workflow ---
    logger.info("=== Simulation: Successful Weather Fetch Workflow ===")
    # Launch the workflow from the initial state and run automatic transitions.
    fsm = await load_fsm()
    current_state = asyncio.create_task(
        flow_processor.run_workflow(fsm=fsm, technical_id=technical_id, entity=chat))

    logger.info(f"Workflow stopped at state: {current_state}")
    #####todo

    return jsonify({"message": "Chat created", "technical_id": technical_id}), 200


# polling for new questions here
@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(seconds=10))
async def get_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    questions_queue = chat.get("questions_queue", {}).get("new_questions", [])
    return await poll_questions(auth_header, chat, questions_queue, technical_id)


@app.route(API_PREFIX + '/chats/<technical_id>/text-questions', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(days=1))
async def submit_question_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)

    req_data = await request.get_json()
    question = req_data.get('question')
    res = await _submit_question_helper(auth_header=auth_header, chat=chat, question=question, technical_id=technical_id)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(days=1))
async def submit_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)

    req_data = await request.form
    req_data = req_data.to_dict()
    question = req_data.get('question')
    file = await request.files
    user_file = file.get('file')
    if user_file.content_length > MAX_FILE_SIZE:
        return {"error": f"File size exceeds {MAX_FILE_SIZE} limit"}
    res = await _submit_question_helper(auth_header=auth_header,
                                        chat=chat,
                                        question=question,
                                        technical_id=technical_id,
                                        user_file=user_file)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/push-notify', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def push_notify(technical_id):
    return jsonify({"error": OPERATION_NOT_SUPPORTED_WARNING}), 400
    # auth_header = request.headers.get('Authorization')
    # chat = await _get_chat_for_user(auth_header, technical_id)
    # await git_pull(chat['chat_id'])
    # return await _submit_answer_helper(technical_id, PUSH_NOTIFICATION, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/approve', methods=['POST'])
@auth_required_to_proceed
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def approve(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    return await _submit_answer_helper(technical_id, APPROVE, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/rollback', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def rollback(technical_id):
    auth_header = request.headers.get('Authorization')
    req_data = await request.get_json()
    if not req_data.get('question') or not req_data.get('stack'):
        return jsonify({"error": ADDITIONAL_QUESTION_ROLLBACK_WARNING}), 400
    question = req_data.get('question') if req_data else None
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    return await rollback_dialogue_script(technical_id, auth_header, chat, question)


@app.route(API_PREFIX + '/chats/<technical_id>/text-answers', methods=['POST'])
@auth_required_to_proceed
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def submit_answer_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    req_data = await request.get_json()
    answer = req_data.get('answer')
    if answer and len(str(answer).encode('utf-8')) > MAX_TEXT_SIZE:
        return jsonify({"error": "Answer size exceeds 1MB limit"}), 400
    return await _submit_answer_helper(technical_id, answer, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/answers', methods=['POST'])
@auth_required_to_proceed
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def submit_answer(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    req_data = await request.form
    req_data = req_data.to_dict()
    answer = req_data.get('answer')

    # Check if a file has been uploaded
    file = await request.files
    user_file = file.get('file')
    if user_file.content_length > MAX_FILE_SIZE:
        return {"error": f"File size exceeds {MAX_FILE_SIZE} limit"}
    return await _submit_answer_helper(technical_id, answer, auth_header, chat, user_file)




async def _get_chat_for_user(auth_header, technical_id, request=None):
    user_id = _get_user_id(auth_header=auth_header)
    if not user_id:
        raise InvalidTokenException()

    chat = await entity_service.get_item(token=auth_header,
                                         entity_model="chat",
                                         entity_version=ENTITY_VERSION,
                                         technical_id=technical_id)

    if not chat and CHAT_REPOSITORY == "local":
        # todo check here
        async with chat_lock:
            chat = await entity_service.get_item(token=auth_header,
                                                 entity_model="chat",
                                                 entity_version=ENTITY_VERSION,
                                                 technical_id=technical_id)
            if not chat:
                await clone_repo(chat_id=technical_id)

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{RAW_REPOSITORY_URL}/{technical_id}/entity/chat.json") as response:
                        data = await response.text()
                chat = json.loads(data)
                if not chat:
                    raise ChatNotFoundException()

                await entity_service.add_item(token=auth_header,
                                              entity_model="chat",
                                              entity_version=ENTITY_VERSION,
                                              entity=chat)

    elif not chat:
        raise ChatNotFoundException()
    # todo concurrent requests might override
    if chat["user_id"] != user_id:
        if chat["user_id"].startswith("guest.") and not user_id.startswith("guest."):
            chat["user_id"] = user_id
            await entity_service.update_item(token=auth_header,
                                             entity_model="chat",
                                             entity_version=ENTITY_VERSION,
                                             technical_id=technical_id,
                                             entity=chat,
                                             meta={})
        else:
            raise InvalidTokenException()

    return chat


def _get_user_id(auth_header):
    try:
        token = auth_header.split(" ")[1]
        # Decode the JWT without verifying the signature
        # The `verify=False` option ensures that we do not verify the signature
        # This is useful for extracting the payload only.
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")
        if user_id.startswith('guest.'):
            validate_token(token)
        return user_id
    except jwt.InvalidTokenError:
        return None


async def _get_chats_by_user_name(auth_header, user_id):
    return await entity_service.get_items_by_condition(token=auth_header,
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


async def _submit_question_helper(auth_header, technical_id, chat, question, user_file=None):
    # Check if a file has been uploaded

    # Validate input
    if not question:
        return jsonify({"message": "Invalid entity"}), 400

    # Return mock response if AI mock mode is enabled
    if MOCK_AI == "true":
        return jsonify({"message": "mock ai answer"}), 200

    # Process file if provided
    if user_file:
        question = await get_user_message(message=question, user_file=user_file)

    # Call AI service with the file
    chat["messages"].append({"role": "user", "content": question})
    result = await ai_agent.run(
            methods_dict=None,
            cls_instance=None,
            entity=chat,
            technical_id=technical_id,
            tools=None,
            model=OPEN_AI,
            tool_choice=None
        )

    return jsonify({"message": result}), 200


async def _submit_answer_helper(technical_id, answer, auth_header, chat, user_file=None):
    question_queue = await _initialize_question_queue(chat=chat)

    if question_queue:
        return jsonify({
            "message": "Could you please have a look at a couple of more questions before submitting your answer?"
        }), 400

    is_valid, validated_answer = _validate_answer(answer=answer, user_file=user_file)
    if not is_valid:
        return jsonify({"message": validated_answer}), 400

    _append_wait_notification(question_queue=question_queue)
    await _update_finished_flow(chat=chat, answer=validated_answer, user_file=user_file)
    _increment_iteration(chat=chat, answer=validated_answer)

    await entity_service.update_item(
        token=auth_header,
        entity_model="chat",
        entity_version=ENTITY_VERSION,
        technical_id=technical_id,
        entity=chat,
        meta={}
    )

    await _trigger_manual_transition(chat=chat, technical_id=technical_id)

    return jsonify({"message": "Answer received"}), 200


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
        if event.get("stack") and (
                not event.get('iteration') or (event.get('iteration') and event.get('iteration') < 2)):
            new_event = copy.deepcopy(event)
            new_event['iteration'] = 0
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


async def _initialize_question_queue(chat):
    chat.setdefault("questions_queue", {}).setdefault("new_questions", [])
    return chat["questions_queue"]["new_questions"]


def _validate_answer(answer, user_file):
    if not answer:
        if not user_file:
            return False, "Invalid entity"
        return True, "please, consider the contents of this file"
    return True, answer


def _append_wait_notification(question_queue):
    wait_notification = {
        "notification": f"Thank you for your answer! {DESIGN_PLEASE_WAIT}",
        "prompt": {},
        "answer": None,
        "function": None,
        "iteration": 0,
        "max_iteration": 0
    }
    question_queue.append(wait_notification)


async def _update_finished_flow(chat, answer, user_file):
    answer = await get_user_message(message=answer, user_file=user_file)
    finished_stack = chat["chat_flow"].setdefault("finished_flow", [])
    finished_stack.append({
        "type": "answer",
        "answer": answer,
        "publish": True,
        "consumed": False
    })


async def get_user_message(message, user_file):
    if user_file:
        file = (await request.files).get('file')
        if file:
            file_contents = read_file_content(file)
            message = f"{message}: {file_contents}" if message else file_contents
    return message


def _increment_iteration(chat, answer):
    if answer == APPROVE:
        transition = chat.get("transition")
        chat["transitions"]["current_iteration"][transition] = MAX_ITERATION+1

async def _trigger_manual_transition(chat, technical_id):
    fsm = await load_fsm()
    current_state = chat.get("current_state")
    state_info = fsm["states"].get(current_state, {})
    manual_events = [
        event for event, transition in state_info.get("transitions", {}).items()
        if transition.get("manual", False)
    ]

    if manual_events:
        asyncio.create_task(flow_processor.trigger_manual_transition(
            current_state=current_state,
            event=manual_events[0],
            entity=chat,
            fsm=fsm,
            technical_id=technical_id
        ))




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
