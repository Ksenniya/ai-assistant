```python
import logging
import asyncio
from dataclasses import dataclass
from quart import Quart, jsonify, request
from quart_schema import QuartSchema, validate_request, validate_querystring
import httpx

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)
QuartSchema(app)

# In-memory cache for processing jobs
entity_job = {}

@dataclass
class ProcessInput:
    input: str

@dataclass
class Calculation:
    operation: str
    numbers: list

@app.route('/hello', methods=['GET'])
async def hello():
    return jsonify(message="Hello, World!")

@app.route('/process', methods=['POST'])
@validate_request(ProcessInput)  # Validation last in POST request
async def process(data: ProcessInput):
    # TODO: Implement actual processing logic
    input_data = data.input
    requested_at = asyncio.get_event_loop().time()
    job_id = len(entity_job) + 1
    entity_job[job_id] = {"status": "processing", "requestedAt": requested_at}
    
    # Fire and forget the processing task
    await asyncio.create_task(process_entity(job_id, input_data))
    
    return jsonify(result=f"Processing {input_data} with job_id {job_id}.")

async def process_entity(job_id, input_data):
    try:
        # Simulate external API call
        async with httpx.AsyncClient() as client:
            # TODO: Replace with actual API call
            response = await client.post('https://api.example.com/process', json={"data": input_data})
            result = response.json()  # Assuming the API returns a JSON response
            logger.info(f"Processed job_id {job_id} with result: {result}")
            entity_job[job_id]['status'] = "completed"
            # TODO: Save or process the result as needed
    except Exception as e:
        logger.exception(e)
        entity_job[job_id]['status'] = "error"

@app.route('/calculate', methods=['POST'])
@validate_request(Calculation)  # Validation last in POST request
async def calculate(data: Calculation):
    operation = data.operation
    numbers = data.numbers
    
    if operation not in ['add', 'subtract', 'multiply', 'divide']:
        return jsonify({"error": "Invalid operation"}), 400
    
    if len(numbers) != 2:
        return jsonify({"error": "Exactly two numbers are required"}), 400
    
    result = None
    if operation == 'add':
        result = numbers[0] + numbers[1]
    elif operation == 'subtract':
        result = numbers[0] - numbers[1]
    elif operation == 'multiply':
        result = numbers[0] * numbers[1]
    elif operation == 'divide':
        if numbers[1] == 0:
            return jsonify({"error": "Division by zero is not allowed"}), 400
        result = numbers[0] / numbers[1]
    
    return jsonify(result=result)

@app.route('/companies/<string:id>/lei', methods=['GET'])
@validate_querystring(ProcessInput)  # Validation first in GET request (workaround)
async def get_leis():
    # Cannot put body to GET request! Only accessing query parameters is allowed.
    # Example: request.args.get('name') for retrieving query parameters
    return jsonify(message="LEI retrieval not implemented yet.")

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
```