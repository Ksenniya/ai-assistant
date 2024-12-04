import json
import queue

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from common.config.config import MOCK_AI, CYODA_AI_API
from common.util.utils import _clean_formatting
from entity.app_builder_job.data.data import stack
from logic.logic import process_dialogue_script
from logic.init import ai_service, cyoda_token, chat_id, question_queue

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

process_dialogue_script()


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/get_question', methods=['GET'])
def get_question():
    try:
        question_for_user = question_queue.get_nowait()
        return jsonify({"question": json.dumps(question_for_user)}), 200
    except queue.Empty:
        return jsonify({"question": None}), 204  # No Content


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    req_data = request.get_json()
    answer = req_data.get('answer')
    if not answer:
        return jsonify({"message": "Invalid entity"}), 400
    # Here, handle the answer (e.g., store it, process it, etc.)
    if not stack:
        return jsonify({"message": "Finished"}), 200
    next_event = stack[-1]
    next_event["answer"] = _clean_formatting(answer)
    process_dialogue_script()
    return jsonify({"message": "Answer received"}), 200


@app.route('/ask_question', methods=['POST'])
def ask_question():
    req_data = request.get_json()
    question = req_data.get('answer')  # todo
    if not question:
        return jsonify({"message": "Invalid entity"}), 400
    # Here, handle the answer (e.g., store it, process it, etc.)
    if not stack:
        return jsonify({"message": "Finished"}), 200
    if MOCK_AI=="true":
        return jsonify({"message": "mock ai answer"}), 200
    result = ai_service.ai_chat(token=cyoda_token, chat_id=chat_id, ai_endpoint=CYODA_AI_API, ai_question=question)
    return jsonify({"message": result}), 200


if __name__ == '__main__':
    app.run(debug=True)
