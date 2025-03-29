```python
from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request, validate_querystring
from dataclasses import dataclass
import httpx
import asyncio
import logging
from datetime import datetime

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a Quart application
app = Quart(__name__)
QuartSchema(app)

# In-memory cache to simulate persistence
entity_job = {}

@dataclass
class ProcessDataInput:
    data_field_1: str
    data_field_2: str

@dataclass
class ResultQuery:
    job_id: str

async def fetch_external_data(data_field_1, data_field_2):
    # TODO: Replace with a real API call
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'https://api.example.com/data?field1={data_field_1}&field2={data_field_2}')
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.exception("HTTP error occurred: %s", e)
            return None  # Handle errors appropriately
        except Exception as e:
            logger.exception("An error occurred: %s", e)
            return None

async def process_entity(job_id, data):
    await asyncio.sleep(2)  # Placeholder for processing time
    processed_value = f"Processed {data['data_field_1']} and {data['data_field_2']}"
    entity_job[job_id]["result"] = processed_value
    entity_job[job_id]["status"] = "completed"

@app.route('/process-data', methods=['POST'])
@validate_request(ProcessDataInput)  # Validation should be last for POST
async def process_data(data: ProcessDataInput):
    job_id = str(datetime.utcnow().timestamp())  # Unique job ID
    requested_at = datetime.utcnow()

    entity_job[job_id] = {"status": "processing", "requestedAt": requested_at}
    
    # Fire and forget the processing task
    await asyncio.create_task(process_entity(job_id, data.__dict__))

    return jsonify({
        "result": None,
        "status": "success",
        "message": "Processing started.",
        "job_id": job_id
    })

@app.route('/results', methods=['GET'])
@validate_querystring(ResultQuery)  # Workaround for validation order issue
async def get_results():
    job_id = request.args.get('job_id')  # Accessing GET parameters
    if job_id:
        return jsonify({
            "results": entity_job.get(job_id, {}),
            "status": "success"
        })
    return jsonify({
        "results": [
            {"id": job_id, **job_info} for job_id, job_info in entity_job.items()
        ],
        "status": "success"
    })

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
```