```markdown
# Functional Requirements Document

## API Endpoints

### 1. GET /results
- **Description**: Retrieve the application results.
- **Request Format**: 
  - Query Parameters:
    - `user_id` (optional): The ID of the user whose results are to be retrieved.
- **Response Format**: 
  - 200 OK
    ```json
    {
        "results": [
            {
                "id": 1,
                "data": "Sample result data"
            },
            ...
        ]
    }
    ```
  - 404 Not Found
    ```json
    {
        "error": "Results not found."
    }
    ```

### 2. POST /calculate
- **Description**: Perform calculations or retrieve external data based on the input provided.
- **Request Format**: 
  - Body:
    ```json
    {
        "input_data": "Data for calculation",
        "user_id": "12345"
    }
    ```
- **Response Format**: 
  - 201 Created
    ```json
    {
        "result": "Calculated result",
        "user_id": "12345"
    }
    ```
  - 400 Bad Request
    ```json
    {
        "error": "Invalid input data."
    }
    ```

## User-App Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant App
    participant ExternalService

    User->>App: POST /calculate
    App->>ExternalService: Request data based on input
    ExternalService-->>App: Return data
    App-->>User: 201 Created with result

    User->>App: GET /results
    App-->>User: 200 OK with results
``` 

```mermaid
journey
    title User Journey for Calculation and Result Retrieval
    section Calculation
      User initiates calculation: 5: User
      App processes calculation: 4: App
      External service responds: 5: ExternalService
      App sends result to user: 5: App
    section Result Retrieval
      User requests results: 5: User
      App retrieves results: 4: App
      App sends results to user: 5: App
``` 
```