import asyncio
import copy
import functools
import logging
import queue

import jwt

from quart import Quart, request, jsonify, send_from_directory, websocket
from quart_cors import cors
from common.config.config import MOCK_AI, CYODA_AI_API, ENTITY_VERSION, API_PREFIX, API_URL
from common.exception.exceptions import ChatNotFoundException, UnauthorizedAccessException
from common.util.utils import clean_formatting, send_get_request, read_file, \
    get_project_file_name
from entity.chat.data.data import app_building_stack, APP_BUILDER_FLOW
from entity.chat.workflow.helper_functions import git_pull
from logic.logic import process_dialogue_script
from logic.init import ai_service, cyoda_token, entity_service

PUSH_NOTIFICATION = "push_notification"
APPROVE = "approved"

logger = logging.getLogger('django')

app = Quart(__name__, static_folder='static', static_url_path='')
app = cors(app, allow_origin="*")


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
        # Check for Authorization header
        auth_header = websocket.headers.get('Authorization') if websocket else request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        token = auth_header.split(" ")[1]

        # Call external service to validate the token
        response = await send_get_request(token, API_URL, "v1")

        if response.get("status") == 401:
            raise UnauthorizedAccessException("Invalid token")

        # If the token is valid, proceed to the requested route
        return await func(*args, **kwargs)

    return wrapper


# @app.websocket(API_PREFIX + '/ws')
# @auth_required
# async def ws():
#     try:
#         while True:
#             # If you need to keep the connection alive
#             # or just block until client disconnects.
#             # If client disconnects, a WebsocketDisconnect will be raised.
#             event = await clients_queue.get()
#             await websocket.send(event)
#     except asyncio.CancelledError:
#         # Handle the cancellation gracefully
#         # You can log the cancellation or perform any other necessary actions
#         pass


# @app.websocket('/ws')
# async def ws():
#     # Receive technical_id from the client when the connection is established
#     technical_id = await websocket.receive()
#
#     # Map the technical_id to the websocket connection
#     clients_map[technical_id] = websocket
#
#     try:
#         while True:
#             # Wait for an event from the queue
#             event = await clients_queue.get()
#
#             # Directly check if there's a client corresponding to the event's id
#             if event['id'] in clients_map:
#                 # Send the event to the client
#                 await clients_map[event['id']].send(event['data'])
#             else:
#                 # If the client is not found (e.g., disconnected), you can log or ignore
#                 pass
#
#     except asyncio.CancelledError:
#         # Handle client disconnection (can clean up if necessary)
#         pass
#     finally:
#         # Clean up when the WebSocket connection is closed
#         if technical_id in clients_map:
#             del clients_map[technical_id]


@app.route('/')
async def index():
    # Ensure that 'index.html' is located in the 'static' folder
    return await send_from_directory(app.static_folder, 'index.html')


def _get_user_id(auth_header):
    try:
        if not auth_header:
            return jsonify({"error": "Invalid token"}), 401
        token = auth_header.split(" ")[1]
        # Decode the JWT without verifying the signature
        # The `verify=False` option ensures that we do not verify the signature
        # This is useful for extracting the payload only.
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("userId")
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


async def _submit_question_helper(chat, question):
    # Check if a file has been uploaded

    if not question:
        return jsonify({"message": "Invalid entity"}), 400
    if MOCK_AI == "true":
        return jsonify({"message": "mock ai answer"}), 200
    result = await ai_service.ai_chat(token=cyoda_token, chat_id=chat["chat_id"], ai_endpoint=CYODA_AI_API,
                                      ai_question=question)
    return jsonify({"message": result}), 200


async def rollback_dialogue_script(technical_id, auth_header, chat, question):
    current_flow = chat["chat_flow"]["current_flow"]
    finished_flow = chat["chat_flow"]["finished_flow"]
    event = finished_flow.pop()
    if question:
        while finished_flow and (not event.get("question") or event.get("question") != question):
            current_flow.append(event)
            event = finished_flow.pop()
    else:
        while finished_flow and (not event.get("function") or event.get("function").get("name") != "refresh_context"):
            current_flow.append(event)
            event = finished_flow.pop()
    current_flow.append(event)
    await entity_service.update_item(token=auth_header,
                                     entity_model="chat",
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=chat,
                                     meta={})
    asyncio.create_task(process_dialogue_script(auth_header, technical_id))
    return jsonify({"message": "Answer received"}), 200


async def _submit_answer_helper(technical_id, answer, auth_header, chat):
    question_queue = chat["questions_queue"]["new_questions"]
    if not question_queue.empty():
        return jsonify({
            "message": "Could you please have a look at a couple of more questions before submitting your answer?"}), 400
    if not answer:
        return jsonify({"message": "Invalid entity"}), 400
    stack = chat["chat_flow"]["current_flow"]
    if not stack:
        return jsonify({"message": "Finished"}), 200
    next_event = stack[-1]
    if answer == PUSH_NOTIFICATION:
        next_event["answer"] = clean_formatting(
            await read_file(get_project_file_name(chat['chat_id'], next_event["file_name"])))
    elif answer == APPROVE:
        next_event["max_iteration"] = -1
    else:
        next_event["answer"] = clean_formatting(answer)
    await entity_service.update_item(token=auth_header,
                                     entity_model="chat",
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=chat,
                                     meta={})
    asyncio.create_task(process_dialogue_script(auth_header, technical_id))
    return jsonify({"message": "Answer received"}), 200
    # await process_dialogue_script(auth_header, technical_id)
    # return await poll_questions(auth_header, chat, question_queue, technical_id)


@app.route(API_PREFIX + '/chat-flow', methods=['GET'])
@auth_required
async def get_chat_flow():
    return jsonify(APP_BUILDER_FLOW)


@app.route(API_PREFIX + '/chats', methods=['GET'])
@auth_required
async def get_chats():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    chats = await entity_service.get_items_by_condition(token=auth_header,
                                                        entity_model="chat",
                                                        entity_version=ENTITY_VERSION,
                                                        condition={"key": "user_id", "value": user_id})
    chats_view = [{
        'technical_id': chat['technical_id'],
        'chat_id': chat['chat_id'],
        'name': chat['name'],
        'description': chat['description'],
        'date': chat['date'],
        'last_modified': chat['last_modified']
    } for chat in chats]

    return jsonify({"chats": chats_view})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['GET'])
@auth_required
async def get_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    dialogue = []
    for item in chat["chat_flow"]["finished_flow"]:
        if item.get("question") or item.get("notification") or item.get("answer"):
            dialogue.append(item)
    chats_view = {
        'technical_id': technical_id,
        'chat_id': chat['chat_id'],
        'name': chat['name'],
        'description': chat['description'],
        'date': chat['date'],
        'last_modified': chat['last_modified'],
        'dialogue': dialogue
    }
    return jsonify({"chat_body": chats_view})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['DELETE'])
@auth_required
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
    new_questions_stack = [
        {
            "notification": "🚀 Please check out your dedicated branch! 🌿 It'll just be you and me contributing to it, so let's make it awesome together! 😄",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },
        {
            "notification": "🎉 Great news! Your application will soon be available on the Cyoda Platform GitHub space! 🚀 Check it out here: [Cyoda Platform GitHub](https://github.com/Cyoda-platform/quart-client-template) 😄",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },
        {
            "notification": "If something goes wrong 😬, don't worry—just roll back! We've got this!",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },
        {
            "notification": "👍 If you're happy with my work or if you'd like me to pull your changes without analyzing them, just send me an approval notification! 😄",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },
        {
            "notification": "📝 If you'd like me to review your update to the remote, just click the push button! I'll fetch your changes and make any adjustments if needed. 😊",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },
        {
            "notification": "Your branch will be ready soon 🔧 When I push my changes to the remote, I'll let you know! If you'd like to suggest any improvements, feel free to send me a message or use Canvas. I'm happy to collaborate! 😊",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },


        {
            "notification": "We'll do our best to support you in building your application and deploying it to Cyoda Cloud! 🌟💻 Feel free to reach out if you need any help along the way! 😊",
            "prompt": {},
            "answer": None,
            "function": None,
            "iteration": 0,
            "file_name": "instruction.txt",
            "max_iteration": 0
        },
        {"notification": "👋 Hello and welcome to the Cyoda Application Builder! 🎉 We're excited to have you on board! Let's build something amazing together! 😄 ",
         "prompt": {},
         "answer": None,
         "function": None,
         "iteration": 0,
         "file_name": "instruction.txt",
         "editable": True,
         "max_iteration": 0
         }]
    new_questions = queue.Queue()
    while new_questions_stack:
        new_questions.put(new_questions_stack.pop())
    chat = {
        "user_id": user_id,
        "date": "2023-11-07T12:00:00Z",
        "last_modified": "2023-11-07T12:00:00Z",
        "questions_queue": {"new_questions": new_questions, "asked_questions": queue.Queue()},
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
async def get_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    question_queue = chat["questions_queue"]["new_questions"]
    return await poll_questions(auth_header, chat, question_queue, technical_id)


# "questions": [
#        {
#            "answer": "",
#            "context": {},
#            "data": {},
#            "entity": {},
#            "file_name": "entity/app_design.json",
#            "flow_step": "gathering requirements",
#            "function": {},
#            "index": 0,
#            "iteration": 2,
#            "max_iteration": 15,
#            "notification": "^_^, I've pushed the changes to entity/app_design.json . Could you please have a look \ud83d\ude38",
#            "prompt": {},
#            "question": ""
#        },
#        {
#            "answer": "",
#            "context": {},
#            "data": {},
#            "entity": {},
#            "file_name": "entity/app_design.json",
#            "flow_step": "gathering requirements",
#            "function": {},
#            "index": 0,
#            "iteration": 1,
#            "max_iteration": 15,
#            "notification": "",
#            "prompt": {},
#            "question": {
#                "can_proceed": false,
#                "questions_to_answer": [
#                    "ToAE4WYJoCX"
#                ]
#            }
#        },
async def poll_questions(auth_header, chat, question_queue, technical_id):
    try:
        questions_to_user = []
        while not question_queue.empty():
            questions_to_user.append(_process_question(question_queue.get_nowait()))
        await entity_service.update_item(token=auth_header,
                                         entity_model="chat",
                                         entity_version=ENTITY_VERSION,
                                         technical_id=technical_id,
                                         entity=chat,
                                         meta={})
        return jsonify({"questions": questions_to_user}), 200
    except queue.Empty:
        return jsonify({"questions": []}), 200  # No Content
    except Exception as e:
        logger.exception(e)
        return jsonify({"questions": []}), 200  # No Content


def _process_question(question):
    if question.get("question") and question.get("ui_config"):
        # Create a deep copy of the question object
        new_question = copy.deepcopy(question)
        result = []

        # Iterating through display_keys in the ui_config
        for key_object in new_question.get("ui_config", {}).get("display_keys", []):
            # Extract the key from the key_object (the dictionary key)
            if isinstance(key_object, dict):
                for key, value in key_object.items():
                    # Append the corresponding value from the "question" dictionary using the extracted key
                    if key in new_question.get("question", {}):
                        result.append(value)
                        result.append(new_question.get("question").get(key))

        # Combine the values into a single string
        new_question["question"] = " ".join(str(item) for item in result)

        return new_question

    # Return the original question if conditions are not met
    return question


@app.route(API_PREFIX + '/chats/<technical_id>/notification', methods=['PUT'])
@auth_required
async def edit_file(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    req_data = await request.get_json()
    #todo
    return jsonify({"questions": []}), 200


@app.route(API_PREFIX + '/chats/<technical_id>/text-questions', methods=['POST'])
@auth_required
async def submit_question_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)

    req_data = await request.get_json()
    question = req_data.get('question')
    res = await _submit_question_helper(chat, question)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['POST'])
@auth_required
async def submit_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)

    req_data = await request.form
    req_data = req_data.to_dict()
    question = req_data.get('question')
    files = await request.files
    files = files.get('file')
    res = await _submit_question_helper(chat, question)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/push-notify', methods=['POST'])
@auth_required
async def push_notify(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    await git_pull(chat['chat_id'])
    return await _submit_answer_helper(technical_id, PUSH_NOTIFICATION, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/approve', methods=['POST'])
@auth_required
async def approve(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    return await _submit_answer_helper(technical_id, APPROVE, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/rollback', methods=['POST'])
@auth_required
async def rollback(technical_id):
    auth_header = request.headers.get('Authorization')
    req_data = await request.get_json()
    question = req_data.get('question') if req_data else None
    chat = await _get_chat_for_user(auth_header, technical_id)
    return await rollback_dialogue_script(technical_id, auth_header, chat, question)


@app.route(API_PREFIX + '/chats/<technical_id>/text-answers', methods=['POST'])
@auth_required
async def submit_answer_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    req_data = await request.get_json()
    answer = req_data.get('answer')
    return await _submit_answer_helper(technical_id, answer, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/answers', methods=['POST'])
@auth_required
async def submit_answer(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(auth_header, technical_id)
    req_data = await request.form
    req_data = req_data.to_dict()
    answer = req_data.get('answer')

    # Check if a file has been uploaded
    file = await request.files
    file = file.get('file')
    return await _submit_answer_helper(technical_id, answer, auth_header, chat)


if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=5000, threaded=True)
