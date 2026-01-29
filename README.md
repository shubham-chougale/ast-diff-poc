# AST Diff POC for Property Files

A proof-of-concept implementation of an AST-based diff engine for Java-style `.properties` files that accurately detects structural code differences including additions, deletions, modifications, moves, and semantic equivalence.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [REST API](#rest-api)
  - [Python API](#python-api)
- [Project Structure](#project-structure)
- [Output Format](#output-format)
- [Testing](#testing)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Limitations](#limitations)
- [Contributing](#contributing)

## 🎯 Overview

This project provides a sophisticated diff engine that analyzes property files at the Abstract Syntax Tree (AST) level, rather than simple text comparison. It can detect:

- **Structural Changes**: Identifies changes at the AST level, not just text differences
- **Move Detection**: Tracks when properties are moved to different line numbers
- **Semantic Equivalence**: Identifies when changes are semantically equivalent (e.g., whitespace-only)
- **Line Number Tracking**: Preserves and reports exact line numbers for all changes
- **Complexity Analysis**: Calculates complexity scores for changes to help prioritize reviews

## ✨ Features

- ✅ **Multiple Change Types**: Supports ADDED, DELETED, MODIFIED, MOVED, MOVED_AND_MODIFIED
- ✅ **AST Normalization**: Normalizes property files before comparison for accurate diff detection
- ✅ **REST API**: FastAPI-based REST API for integration with other systems
- ✅ **CLI Tool**: Command-line interface for quick diff computation
- ✅ **Complexity Scoring**: Analyzes change complexity to help prioritize reviews
- ✅ **File Upload Support**: API supports both JSON content and file uploads
- ✅ **Comprehensive Testing**: Test suite with multiple sample files
- ✅ **Interactive Documentation**: Swagger UI and ReDoc for API exploration

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

### Setup Steps

1. **Install Poetry** (if not already installed):
   ```bash
   pip install poetry
   ```

2. **Clone or navigate to the project directory**:
   ```bash
   cd ast-diff-poc
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

## 💻 Usage

### Command Line Interface

The simplest way to use the POC is through the CLI:

```bash
ast-diff source.properties target.properties
```

**Options:**
- `--output, -o`: Save output to a file (default: stdout)
- `--no-normalize`: Disable AST normalization before comparison
- `--pretty`: Pretty-print JSON output
- `--no-complexity`: Disable complexity calculation

**Example:**
```bash
ast-diff source.properties target.properties --output diff.json --pretty
```

### REST API

#### Starting the API Server

**Option 1: Using the script**
```bash
poetry run python scripts/run_api.py
```

**Option 2: Using uvicorn directly**
```bash
poetry run uvicorn ast_diff_poc.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: Using the CLI script**
```bash
poetry run ast-diff-api
```

The API will be available at `http://localhost:8000`

#### API Endpoints

**Health Check**
```bash
GET /api/health
```

**Compute Diff from Content**
```bash
POST /api/diff
Content-Type: application/json

{
  "source_content": "key1=value1\nkey2=value2",
  "target_content": "key1=value1\nkey2=value3",
  "normalize": true,
  "source_file_name": "source.properties",
  "target_file_name": "target.properties"
}
```

**Compute Diff from Files**
```bash
POST /api/diff/files
Content-Type: multipart/form-data

source_file: [file]
target_file: [file]
normalize: true
calculate_complexity: false
```

**Compute Complexity**
```bash
POST /api/complexity
POST /api/complexity/files
```

#### Interactive API Documentation

Once the server is running, access interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

#### Example API Usage

**Using curl:**
```bash
# JSON content
curl -X POST "http://localhost:8000/api/diff" \
  -H "Content-Type: application/json" \
  -d '{
    "source_content": "key1=value1\nkey2=value2",
    "target_content": "key1=value1\nkey2=value3",
    "normalize": true
  }'

# File upload
curl -X POST "http://localhost:8000/api/diff/files?normalize=true" \
  -F "source_file=@source.properties" \
  -F "target_file=@target.properties"
```

**Using Python requests:**
```python
import requests

url = "http://localhost:8000/api/diff"
data = {
    "source_content": "key1=value1\nkey2=value2",
    "target_content": "key1=value1\nkey2=value3",
    "normalize": True
}
response = requests.post(url, json=data)
print(response.json())
```

### Python API

```python
from ast_diff_poc.diff.diff_engine import DiffEngine
from ast_diff_poc.utils.file_loader import load_property_file

# Load property files
source_ast = load_property_file("source.properties")
target_ast = load_property_file("target.properties")

# Compute diff
engine = DiffEngine(normalize=True, calculate_complexity=True)
result = engine.compute_diff(source_ast, target_ast)

# Access results
print(f"Total changes: {len(result.changes)}")
print(f"Added: {result.summary.added}")
print(f"Deleted: {result.summary.deleted}")
print(f"Modified: {result.summary.modified}")
print(f"Moved: {result.summary.moved}")

# Convert to JSON
import json
print(json.dumps(result.to_dict(), indent=2))
```

### Running the POC on Test Samples

To run the POC on all test samples:

```bash
python scripts/run_poc.py
```

This will process all sample files in `tests/fixtures/` and save results to `output/`.

To generate a summary report:

```bash
python scripts/generate_test_results.py
```

## 📁 Project Structure

```
ast-diff-poc/
├── pyproject.toml              # Poetry configuration
├── README.md                   # This file
├── src/
│   └── ast_diff_poc/
│       ├── __init__.py
│       ├── api/                # FastAPI REST API
│       │   ├── main.py         # FastAPI app initialization
│       │   ├── routes/         # API route definitions
│       │   ├── controllers/    # HTTP request/response handling
│       │   ├── services/       # Business logic
│       │   ├── repositories/   # Data access layer
│       │   └── schemas/        # Request/Response models
│       ├── parser/             # AST parsing
│       │   ├── ast_parser.py   # AST parsing for .properties files
│       │   └── normalization.py # Normalize AST to internal format
│       ├── diff/               # Diff engine
│       │   ├── diff_engine.py  # Core diff detection logic
│       │   └── matcher.py      # Match nodes between source/target
│       ├── models/             # Domain models
│       │   ├── ast_node.py     # AST node data structures
│       │   └── diff_result.py # Diff result data structures
│       ├── complexity/         # Complexity analysis
│       │   └── property_complexity.py
│       ├── utils/              # Utilities
│       │   ├── file_loader.py  # Load and parse property files
│       │   └── logger.py       # Logging utilities
│       └── cli.py              # CLI interface
├── tests/                      # Test suite
│   ├── test_parser.py
│   ├── test_diff_engine.py
│   ├── test_normalization.py
│   ├── test_matcher.py
│   └── fixtures/              # Test sample files
│       ├── sample1/
│       ├── sample2/
│       └── ...
├── docs/                       # Documentation
│   ├── api_architecture.md
│   ├── api_reference.md
│   ├── api_usage.md
│   ├── findings.md
│   ├── normalization_model.md
│   └── examples/
├── output/                     # Generated output files
└── scripts/                    # Utility scripts
    ├── run_api.py
    ├── test_api.py
    └── generate_test_results.py
```

## 📊 Output Format

The diff output is a JSON object with the following structure:

```json
{
  "source_file": "path/to/source.properties",
  "target_file": "path/to/target.properties",
  "changes": [
    {
      "type": "MOVED",
      "key": "FND_MULTIROW_NUMBER_OF_ROWS_PER_PAGE",
      "source_line": 1,
      "target_line": 2,
      "source_value": "1",
      "target_value": "1"
    },
    {
      "type": "MODIFIED",
      "key": "accissues",
      "source_line": 5,
      "target_line": 4,
      "source_value": "Issues",
      "target_value": "Issues & Findings"
    }
  ],
  "summary": {
    "added": 5,
    "deleted": 2,
    "modified": 3,
    "moved": 4,
    "moved_and_modified": 1
  }
}
```

### Change Types

- **ADDED**: Property exists in target but not in source
- **DELETED**: Property exists in source but not in target
- **MODIFIED**: Same key, different value, same line position
- **MOVED**: Same key and value, different line numbers
- **MOVED_AND_MODIFIED**: Same key, different value, different line numbers

## 🧪 Testing

Run the test suite:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=src/ast_diff_poc --cov-report=html
```

Run specific test file:

```bash
poetry run pytest tests/test_diff_engine.py
```

## 🏗️ Architecture

The project follows an MVC-inspired layered architecture:

### API Layer (FastAPI)

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
│  - Data transformation                                  │
├─────────────────────────────────────────────────────────┤
│  Models (Domain Models)                                 │
│  - AST nodes                                           │
│  - Diff results                                        │
│  - Change types                                        │
└─────────────────────────────────────────────────────────┘
```

### Core Components

- **Model Layer**: Data structures (AST nodes, diff results)
- **Controller Layer**: Business logic (parser, diff engine, matcher)
- **View Layer**: CLI interface and output formatting

### Data Flow

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

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Architecture](docs/api_architecture.md)**: Detailed architecture overview
- **[API Reference](docs/api_reference.md)**: Complete API documentation
- **[API Usage Guide](docs/api_usage.md)**: Step-by-step API usage examples
- **[Findings](docs/findings.md)**: Research findings, limitations, and recommendations
- **[Normalization Model](docs/normalization_model.md)**: Normalization approach and rules
- **[Sample Outputs](docs/examples/sample_outputs.json)**: Example diff outputs

## ⚠️ Limitations

See [Findings](docs/findings.md) for detailed limitations. Key points:

- Duplicate key handling may need improvement
- Very large files (>10K properties) may have performance issues
- Comments are parsed but changes not fully tracked
- Encoding detection is basic (UTF-8 and ISO-8859-1 supported)

## 🤝 Contributing

This is a POC project. For production use, consider:

1. Enhanced error handling
2. Performance optimization for large files
3. Better duplicate key handling
4. Comment change tracking
5. Visual diff output
6. Batch processing capabilities
7. Caching mechanisms

## 📝 Acceptance Criteria Status

- ✅ **AC1**: Parser evaluation documented in `docs/findings.md`
- ✅ **AC2**: Normalization model documented in `docs/normalization_model.md`
- ✅ **AC3**: All change types implemented (ADDED, DELETED, MODIFIED, MOVED, MOVED_AND_MODIFIED)
- ✅ **AC5**: Tested with 5+ sample files
- ✅ **AC6**: Limitations documented in `docs/findings.md`
- ✅ **AC7**: Sample outputs in `docs/examples/sample_outputs.json`
- ✅ **AC8**: Complete documentation provided

## 📄 License

This is a proof-of-concept implementation for research purposes.

## 📧 Contact

For questions or issues, please refer to the project documentation or create an issue in the project repository.

---

**Version**: 1.0.0  
**Last Updated**: 2024
