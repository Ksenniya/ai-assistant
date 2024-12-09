import queue
import threading

import jwt

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from common.config.config import MOCK_AI, CYODA_AI_API, ENTITY_VERSION, API_PREFIX
from common.exception.exceptions import ChatNotFoundException, UnauthorizedAccessException
from common.util.utils import _clean_formatting, generate_uuid
from entity.chat.data.data import app_building_stack
from logic.logic import process_dialogue_script
from logic.init import ai_service, cyoda_token, entity_service

app = Flask(__name__, static_folder='static')

CORS(app)  # Enable CORS for all routes


@app.route(API_PREFIX + '/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


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


def _get_chat_for_user(auth_header, technical_id):
    user_id = _get_user_id(auth_header)
    if not user_id:
        raise UnauthorizedAccessException()

    chat = entity_service.get_item(token=auth_header,
                                   entity_model="chat",
                                   entity_version=ENTITY_VERSION,
                                   technical_id=technical_id)

    if not chat:
        raise ChatNotFoundException()

    if chat["user_id"] != user_id:
        raise UnauthorizedAccessException()

    return chat


def _submit_question_helper(chat, question):
    # Check if a file has been uploaded

    if not question:
        return jsonify({"message": "Invalid entity"}), 400
    if MOCK_AI == "true":
        return jsonify({"message": "mock ai answer"}), 200
    result = ai_service.ai_chat(token=cyoda_token, chat_id=chat["chat_id"], ai_endpoint=CYODA_AI_API,
                                ai_question=question)
    return jsonify({"message": result}), 200


def _submit_answer_helper(technical_id, answer, auth_header, chat):
    question_queue = chat["questions_queue"]["new_questions"]
    if not question_queue.empty():
        return jsonify({"message": "Could you please have a look at a couple of more questions before submitting your answer?"}), 400
    if not answer:
        return jsonify({"message": "Invalid entity"}), 400
    stack = chat["chat_flow"]["current_flow"]
    if not stack:
        return jsonify({"message": "Finished"}), 200
    next_event = stack[-1]
    next_event["answer"] = _clean_formatting(answer)
    entity_service.update_item(token=auth_header,
                               entity_model="chat",
                               entity_version=ENTITY_VERSION,
                               technical_id=technical_id,
                               entity=chat,
                               meta={})
    thread = threading.Thread(target=process_dialogue_script, args=(auth_header, technical_id))
    thread.start()
    return jsonify({"message": "Answer received"}), 200


@app.route(API_PREFIX + '/chats', methods=['GET'])
def get_chats():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    chats = entity_service.get_items_by_condition(token=auth_header,
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
def get_chat(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    dialogue = []
    for item in chat["chat_flow"]["finished_flow"]:
        if item.get("question"):
            dialogue.append({"question": item.get("question"), "answer": item.get("answer")})
        elif item.get("answer"):
            dialogue.append({"question": item.get("question"), "answer": item.get("answer")})
        elif item.get("notification"):
            dialogue.append({"question": item.get("notification"), "answer": item.get("answer")})
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
def delete_chat(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    entity_service.delete_item(token=auth_header,
                               entity_model="chat",
                               entity_version=ENTITY_VERSION,
                               technical_id=technical_id,
                               meta={})

    return jsonify({"message": "Chat deleted", "technical_id": technical_id})


@app.route(API_PREFIX + '/chats', methods=['POST'])
def add_chat():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    req_data = request.get_json()
    name = req_data.get('name')
    description = req_data.get('description')
    if not name:
        return jsonify({"message": "Invalid chat name"}), 400
    # Here, handle the answer (e.g., store it, process it, etc.)
    chat = {"user_id": user_id,
            "chat_id": generate_uuid(),
            "date": "2023-11-07T12:00:00Z",
            "last_modified": "2023-11-07T12:00:00Z",
            "questions_queue": {"new_questions": queue.Queue(), "asked_questions": queue.Queue()},
            "chat_flow": {"current_flow": app_building_stack, "finished_flow": []},
            "name": name,
            "description": description}
    technical_id = entity_service.add_item(token=auth_header,
                            entity_model="chat",
                            entity_version=ENTITY_VERSION,
                            entity=chat)
    process_dialogue_script(auth_header, technical_id)
    return jsonify({"message": "Chat created", "technical_id": technical_id}), 200


# polling for new questions here
@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['GET'])
def get_question(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    question_queue = chat["questions_queue"]["new_questions"]
    try:
        questions_to_user = []
        while not question_queue.empty():
            questions_to_user.append(question_queue.get_nowait())
        entity_service.update_item(token=auth_header,
                                   entity_model="chat",
                                   entity_version=ENTITY_VERSION,
                                   technical_id=technical_id,
                                   entity=chat,
                                   meta={})
        return jsonify({"questions": questions_to_user}), 200
    except queue.Empty:
        return jsonify({"questions": None}), 204  # No Content


@app.route(API_PREFIX + '/chats/<technical_id>/text-questions', methods=['POST'])
def submit_question_text(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    req_data = request.get_json()
    question = req_data.get('question')
    return _submit_question_helper(chat, question)

@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['POST'])
def submit_question(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    req_data = request.form.to_dict()
    question = req_data.get('question')
    file = request.files.get('file')

    return _submit_question_helper(chat, question)


@app.route(API_PREFIX + '/chats/<technical_id>/text-answers', methods=['POST'])
def submit_answer_text(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    req_data = request.get_json()
    answer = req_data.get('answer')
    return _submit_answer_helper(technical_id, answer, auth_header, chat)


@app.route(API_PREFIX + '/chats/<technical_id>/answers', methods=['POST'])
def submit_answer(technical_id):
    try:
        auth_header = request.headers.get('Authorization')
        chat = _get_chat_for_user(auth_header, technical_id)
    except UnauthorizedAccessException as e:
        return jsonify({"error": str(e)}), 401
    except ChatNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    req_data = request.form.to_dict()
    answer = req_data.get('answer')

    # Check if a file has been uploaded
    file = request.files.get('file')
    return _submit_answer_helper(technical_id, answer, auth_header, chat)



if __name__ == '__main__':
    app.run(debug=True)
