```python
from quart import Quart, request
from quart_schema import QuartSchema, validate_request, validate_querystring
from dataclasses import dataclass
import asyncio
import logging
from common.config.config import ENTITY_VERSION
from common.repository.cyoda.cyoda_init import init_cyoda
from app_init.app_init import entity_service, cyoda_token

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# Example data class for validation
@dataclass
class Todo:
    task: str

@app.before_serving
async def startup():
    await init_cyoda(cyoda_token)

# POST request to create a todo
@app.route("/test", methods=["POST"])  # This line should go first in post method
@validate_request(Todo)  # This line should go second in post method
async def create_todo(data: Todo):
    try:
        job_id = "some_unique_job_id"  # Placeholder for actual job ID
        entity_job = {}
        entity_job[job_id] = {"status": "processing"}
        # Fire and forget the processing task
        await asyncio.create_task(process_entity(entity_job, data.__dict__))
        
        # Call external service to add the item
        id = await entity_service.add_item(
            token=cyoda_token,
            entity_model="todo",
            entity_version=ENTITY_VERSION,
            entity=data.__dict__
        )
        return {"job_id": job_id, "id": id}, 202
    except Exception as e:
        logger.exception(e)
        return {"error": "Failed to create todo"}, 500

# GET request to retrieve a todo
@app.route("/test", methods=["GET"])  # This line should go first in get method
@validate_querystring(Todo)  # This line should go first in get method
async def get_todo():
    name = request.args.get('name')  # Use standard approach to access parameters values for GET requests
    try:
        # Call external service to retrieve the item
        items = await entity_service.get_items_by_condition(
            token=cyoda_token,
            entity_model="todo",
            entity_version=ENTITY_VERSION,
            condition={"task": name}
        )
        return {"tasks": items}, 200
    except Exception as e:
        logger.exception(e)
        return {"error": "Failed to retrieve todos"}, 500

# GET request with path parameter
@app.route("/companies/<string:id>/lei", methods=["GET"])  # No validation needed
async def get_company_lei(id):
    try:
        # Call external service to retrieve company LEI
        lei_item = await entity_service.get_item(
            token=cyoda_token,
            entity_model="company",
            entity_version=ENTITY_VERSION,
            technical_id=id
        )
        return {"id": id, "lei": lei_item["lei"]}, 200
    except Exception as e:
        logger.exception(e)
        return {"error": "Failed to retrieve company LEI"}, 500

async def process_entity(entity_job, data):
    # TODO: Implement processing logic here
    pass

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
```