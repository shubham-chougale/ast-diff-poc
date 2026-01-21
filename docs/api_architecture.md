# API Architecture - MVC Design Pattern

## Overview

The API follows a clean MVC (Model-View-Controller) architecture pattern with additional layers for separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                  │
├─────────────────────────────────────────────────────────┤
│  Routes (API Endpoints)                                 │
│  - Define HTTP endpoints                                │
│  - Handle routing                                       │
│  - Input validation (via Pydantic)                      │
├─────────────────────────────────────────────────────────┤
│  Controllers (Request/Response Handling)                │
│  - Process HTTP requests                                │
│  - Call services                                        │
│  - Format responses                                     │
│  - Error handling                                       │
├─────────────────────────────────────────────────────────┤
│  Services (Business Logic)                              │
│  - Implement business rules                             │
│  - Orchestrate operations                               │
│  - Call repositories                                    │
├─────────────────────────────────────────────────────────┤
│  Repositories (Data Access)                             │
│  - Parse property files                                 │
│  - Handle file I/O                                      │
│  - Data transformation                                 │
├─────────────────────────────────────────────────────────┤
│  Models (Domain Models)                                 │
│  - AST nodes                                           │
│  - Diff results                                        │
│  - Change types                                        │
└─────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Routes (`api/routes/`)

**Purpose**: Define API endpoints and HTTP routing

**Responsibilities**:
- Define URL paths and HTTP methods
- Register endpoints with FastAPI router
- Accept HTTP requests
- Delegate to controllers

**Example**: `diff_routes.py`
```python
@router.post("/api/diff", response_model=DiffResponse)
async def compute_diff_from_content(request: DiffRequest):
    return controller.compute_diff_from_content(request)
```

### 2. Controllers (`api/controllers/`)

**Purpose**: Handle HTTP request/response logic

**Responsibilities**:
- Validate incoming requests
- Call appropriate services
- Convert domain models to response schemas
- Handle HTTP exceptions
- Format error responses

**Example**: `diff_controller.py`
```python
def compute_diff_from_content(self, request: DiffRequest) -> DiffResponse:
    result = self.service.compute_diff_from_content(...)
    return self._convert_to_response(result)
```

### 3. Services (`api/services/`)

**Purpose**: Implement business logic

**Responsibilities**:
- Orchestrate business operations
- Coordinate between repositories and domain logic
- Apply business rules
- Call diff engine
- Return domain models

**Example**: `diff_service.py`
```python
def compute_diff_from_content(self, ...) -> DiffResult:
    source_ast = self.repository.parse_from_string(...)
    target_ast = self.repository.parse_from_string(...)
    engine = DiffEngine(normalize=normalize)
    return engine.compute_diff(source_ast, target_ast)
```

### 4. Repositories (`api/repositories/`)

**Purpose**: Data access layer

**Responsibilities**:
- Parse property files from various sources (file, string, bytes)
- Handle encoding issues
- Abstract data access details
- Return domain models (ASTs)

**Example**: `property_repository.py`
```python
def parse_from_string(self, content: str, ...) -> PropertyFileAST:
    return self.parser.parse_string(content, file_path)
```

### 5. Schemas (`api/schemas/`)

**Purpose**: Request/Response data models

**Responsibilities**:
- Define API contract (request/response shapes)
- Validate input data
- Serialize/deserialize JSON
- Document API (via Pydantic)

**Example**: `diff_schemas.py`
```python
class DiffRequest(BaseModel):
    source_content: str
    target_content: str
    normalize: bool = True
```

## Data Flow

```
HTTP Request
    ↓
Routes (diff_routes.py)
    ↓
Controllers (diff_controller.py)
    ↓
Services (diff_service.py)
    ↓
Repositories (property_repository.py)
    ↓
Domain Models (AST, DiffResult)
    ↓
Services (process with DiffEngine)
    ↓
Controllers (convert to response schema)
    ↓
Routes (return HTTP response)
    ↓
HTTP Response
```

## Benefits of This Architecture

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Testability**: Each layer can be tested independently
3. **Maintainability**: Changes in one layer don't affect others
4. **Scalability**: Easy to add new endpoints, services, or repositories
5. **Reusability**: Services and repositories can be reused across different controllers
6. **Dependency Injection**: Controllers and services accept dependencies, making testing easier

## Adding New Features

To add a new feature (e.g., batch diff processing):

1. **Add Schema**: Create request/response models in `schemas/`
2. **Add Repository Method**: If new data access needed, add to `repositories/`
3. **Add Service Method**: Implement business logic in `services/`
4. **Add Controller Method**: Handle HTTP in `controllers/`
5. **Add Route**: Define endpoint in `routes/`

## File Structure

```
ast_diff_poc/
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── routes/
│   │   ├── __init__.py
│   │   └── diff_routes.py         # API route definitions
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── diff_controller.py     # HTTP request/response handling
│   ├── services/
│   │   ├── __init__.py
│   │   └── diff_service.py        # Business logic
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── property_repository.py # Data access
│   └── schemas/
│       ├── __init__.py
│       └── diff_schemas.py        # Request/Response models
├── models/                         # Domain models (existing)
├── diff/                           # Diff engine (existing)
├── parser/                         # Parser (existing)
└── utils/                          # Utilities (existing)
```
