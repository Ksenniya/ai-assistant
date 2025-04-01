```python
from quart import Quart, request
from quart_schema import QuartSchema, validate_request, validate_querystring
from dataclasses import dataclass
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# Example data class for validation
@dataclass
class Todo:
    task: str

# POST request to create a todo
@app.route("/test", methods=["POST"])  # This line should go first in post method
@validate_request(Todo)  # This line should go second in post method
async def create_todo(data: Todo):
    requested_at = "2023-10-01T12:00:00Z"  # Placeholder for actual timestamp
    job_id = "some_unique_job_id"  # Placeholder for actual job ID
    entity_job = {}
    entity_job[job_id] = {"status": "processing", "requestedAt": requested_at}
    # Fire and forget the processing task
    await asyncio.create_task(process_entity(entity_job, data.__dict__))
    return {"job_id": job_id}, 202

# GET request to retrieve a todo
@app.route("/test", methods=["GET"])  # This line should go first in get method
@validate_querystring(Todo)  # This line should go first in get method
async def get_todo():
    # Cannot put body to GET request
    name = request.args.get('name')  # Use standard approach to access parameters values for GET requests
    # TODO: Implement retrieval of todo based on name
    return {"task": name}, 200

# GET request with path parameter
@app.route("/companies/<string:id>/lei", methods=["GET"])  # No validation needed
async def get_company_lei(id):
    # TODO: Implement retrieval of company LEI based on id
    return {"id": id, "lei": "some_lei_value"}, 200

async def process_entity(entity_job, data):
    # TODO: Implement processing logic here
    pass

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
```