Here's a prototype implementation for your Quart application based on the specified requirements. The code is structured to be a working prototype, utilizing real APIs where appropriate, while placeholders and mocks are included to indicate areas that may need further development.

```python
from quart import Quart, request, jsonify
from quart_schema import QuartSchema
import httpx
import asyncio
import logging

app = Quart(__name__)
QuartSchema(app)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Local cache to simulate persistence
entity_job = {}

# Mock external API URL (replace with a real API)
EXTERNAL_API_URL = "https://api.example.com/data"  # TODO: Replace with a real API endpoint

async def fetch_external_data(input_data):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_URL, params={"input": input_data})
            response.raise_for_status()
            return response.json()  # Assume the API returns JSON data
    except Exception as e:
        logger.exception("Error fetching external data")
        return None

async def process_entity(job_id, input_data):
    # Simulate processing of the entity
    await asyncio.sleep(2)  # Simulate time-consuming task
    result = f"Processed {input_data}"  # TODO: Replace with actual processing logic
    entity_job[job_id]["status"] = "completed"
    entity_job[job_id]["result"] = result

@app.route('/calculate', methods=['POST'])
async def calculate():
    data = await request.get_json()
    
    user_id = data.get("user_id")
    input_data = data.get("input_data")

    if not input_data:
        return jsonify({"error": "Invalid input data."}), 400

    job_id = len(entity_job) + 1
    requested_at = asyncio.get_event_loop().time()
    
    entity_job[job_id] = {"status": "processing", "requestedAt": requested_at}
    
    # Fire and forget the processing task
    await asyncio.create_task(process_entity(job_id, input_data))

    # Fetch external data if necessary
    external_data = await fetch_external_data(input_data)  # TODO: Use external data in processing if needed

    return jsonify({"result": "Calculation initiated", "user_id": user_id, "job_id": job_id}), 201

@app.route('/results', methods=['GET'])
async def get_results():
    user_id = request.args.get('user_id')
    results = [job for job_id, job in entity_job.items() if job.get("user_id") == user_id] if user_id else list(entity_job.values())
    
    if not results:
        return jsonify({"error": "Results not found."}), 404

    return jsonify({"results": results}), 200

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
```

### Notes:
- The `fetch_external_data` function is a placeholder for making real API calls. You should replace the `EXTERNAL_API_URL` with an actual endpoint.
- The processing logic in `process_entity` is currently a simple placeholder. You can update it as per the actual business logic required.
- The logging setup is included to capture any errors or information during the execution of the application.
- Local caching is simulated using a Python dictionary to hold job statuses and results. No persistent storage is implemented in this prototype.
- The prototype is designed to test the user experience and identify any gaps in requirements before moving towards a more comprehensive solution.