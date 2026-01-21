# API Usage Guide

## Overview

The AST Diff API provides REST endpoints for computing AST-based diffs between Java-style property files. The API follows an MVC (Model-View-Controller) architecture pattern.

## Architecture

The API is structured as follows:

```
api/
├── main.py              # FastAPI application entry point
├── routes/              # Route definitions (API endpoints)
│   └── diff_routes.py
├── controllers/         # Controllers (HTTP request/response handling)
│   └── diff_controller.py
├── services/            # Services (Business logic)
│   └── diff_service.py
├── repositories/        # Repositories (Data access layer)
│   └── property_repository.py
└── schemas/             # Pydantic models (Request/Response schemas)
    └── diff_schemas.py
```

## Running the API

### Option 1: Using the script
```bash
cd ast-diff-poc
poetry run python scripts/run_api.py
```

### Option 2: Using uvicorn directly
```bash
cd ast-diff-poc
poetry run uvicorn ast_diff_poc.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using the CLI script (after installation)
```bash
poetry run ast-diff-api
```

The API will be available at `http://localhost:8000`

## Exposing with ngrok

1. Install ngrok from https://ngrok.com/download

2. Start the API server (see above)

3. In a new terminal, run:
```bash
ngrok http 8000
```

4. Copy the public URL (e.g., `https://abc123.ngrok-free.app`)

## API Endpoints

### Health Check

**GET** `/api/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Compute Diff from Content

**POST** `/api/diff`

Compute diff between two property file contents provided as JSON.

**Request Body:**
```json
{
  "source_content": "key1=value1\nkey2=value2",
  "target_content": "key1=value1\nkey2=value3",
  "normalize": true,
  "source_file_name": "source.properties",
  "target_file_name": "target.properties"
}
```

**Response:**
```json
{
  "source_file": "source.properties",
  "target_file": "target.properties",
  "changes": [
    {
      "type": "MODIFIED",
      "key": "key2",
      "source_line": 2,
      "target_line": 2,
      "source_value": "value2",
      "target_value": "value3"
    }
  ],
  "summary": {
    "added": 0,
    "deleted": 0,
    "modified": 1,
    "moved": 0,
    "moved_and_modified": 0
  }
}
```

### Compute Diff from Files

**POST** `/api/diff/files`

Compute diff between two uploaded property files.

**Request:**
- `source_file`: Multipart file upload (source property file)
- `target_file`: Multipart file upload (target property file)
- `normalize`: Form field (boolean, default: true)

**Response:** Same as `/api/diff`

## Example Usage

### Using curl

**JSON Content:**
```bash
curl -X POST "http://localhost:8000/api/diff" \
  -H "Content-Type: application/json" \
  -d '{
    "source_content": "key1=value1\nkey2=value2",
    "target_content": "key1=value1\nkey2=value3",
    "normalize": true
  }'
```

**File Upload:**
```bash
curl -X POST "http://localhost:8000/api/diff/files?normalize=true" \
  -F "source_file=@source.properties" \
  -F "target_file=@target.properties"
```

### Using Python requests

```python
import requests

# JSON content
url = "http://localhost:8000/api/diff"
data = {
    "source_content": "key1=value1\nkey2=value2",
    "target_content": "key1=value1\nkey2=value3",
    "normalize": True
}
response = requests.post(url, json=data)
print(response.json())

# File upload
url = "http://localhost:8000/api/diff/files"
files = {
    "source_file": open("source.properties", "rb"),
    "target_file": open("target.properties", "rb")
}
data = {"normalize": True}
response = requests.post(url, files=files, data=data)
print(response.json())
```

### Using JavaScript (fetch)

```javascript
// JSON content
const response = await fetch('http://localhost:8000/api/diff', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    source_content: 'key1=value1\nkey2=value2',
    target_content: 'key1=value1\nkey2=value3',
    normalize: true
  })
});

const result = await response.json();
console.log(result);

// File upload
const formData = new FormData();
formData.append('source_file', sourceFile);
formData.append('target_file', targetFile);
formData.append('normalize', 'true');

const response = await fetch('http://localhost:8000/api/diff/files', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

## API Documentation

Once the server is running, you can access interactive API documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input (e.g., malformed property file)
- `500 Internal Server Error`: Server error

Error responses follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Change Types

The API detects the following change types:

- **ADDED**: Property exists in target but not in source
- **DELETED**: Property exists in source but not in target
- **MODIFIED**: Same key, different value, same line position
- **MOVED**: Same key and value, different line numbers
- **MOVED_AND_MODIFIED**: Same key, different value, different line numbers
