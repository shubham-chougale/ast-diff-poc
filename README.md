# AST Diff POC for Property Files

A proof-of-concept implementation of an AST-based diff engine for Java-style `.properties` files that accurately detects structural code differences including additions, deletions, modifications, moves, and semantic equivalence.

## Overview

This POC implements a custom AST parser and diff engine specifically designed for property files. It provides:

- **Structural Diff Detection**: Detects changes at the AST level, not just text differences
- **Move Detection**: Tracks when properties are moved to different line numbers
- **Semantic Equivalence**: Identifies when changes are semantically equivalent (e.g., whitespace-only)
- **Line Number Tracking**: Preserves and reports exact line numbers for all changes
- **Comprehensive Change Types**: Supports ADDED, DELETED, MODIFIED, MOVED, MOVED_AND_MODIFIED

## Project Structure

```
ast-diff-poc/
├── pyproject.toml              # Poetry configuration
├── README.md                    # This file
├── src/
│   └── ast_diff_poc/
│       ├── __init__.py
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── ast_parser.py          # AST parsing for .properties files
│       │   └── normalization.py      # Normalize AST to internal format
│       ├── diff/
│       │   ├── __init__.py
│       │   ├── diff_engine.py         # Core diff detection logic
│       │   ├── matcher.py             # Match nodes between source/target
│       │   └── change_types.py       # Enum for change types
│       ├── models/
│       │   ├── __init__.py
│       │   ├── ast_node.py            # AST node data structures
│       │   └── diff_result.py        # Diff result data structures
│       ├── utils/
│       │   ├── __init__.py
│       │   └── file_loader.py        # Load and parse property files
│       └── cli.py                     # CLI interface for testing
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_diff_engine.py
│   ├── test_normalization.py
│   ├── test_matcher.py
│   └── fixtures/
│       ├── sample1/
│       │   ├── source.properties
│       │   └── target.properties
│       ├── sample2/
│       │   ├── source.properties
│       │   └── target.properties
│       ├── sample3/
│       │   ├── source.properties
│       │   └── target.properties
│       ├── sample4/
│       │   ├── source.properties
│       │   └── target.properties
│       ├── sample5/
│       │   ├── source.properties
│       │   └── target.properties
│       └── expected_results/
├── docs/
│   ├── findings.md
│   ├── normalization_model.md
│   ├── api_reference.md
│   └── examples/
│       └── sample_outputs.json
├── output/
│   └── .gitkeep
└── scripts/
    ├── run_poc.py
    └── generate_test_results.py
```

## Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

### Setup

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

## Usage

### Command Line Interface

The simplest way to use the POC is through the CLI:

```bash
ast-diff source.properties target.properties
```

**Options:**
- `--output, -o`: Save output to a file (default: stdout)
- `--no-normalize`: Disable AST normalization before comparison
- `--pretty`: Pretty-print JSON output

**Example:**
```bash
ast-diff source.properties target.properties --output diff.json --pretty
```

### Python API

```python
from ast_diff_poc.diff.diff_engine import DiffEngine
from ast_diff_poc.utils.file_loader import load_property_file

# Load property files
source_ast = load_property_file("source.properties")
target_ast = load_property_file("target.properties")

# Compute diff
engine = DiffEngine()
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

## Output Format

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

## Testing

Run the test suite:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=src/ast_diff_poc --cov-report=html
```

## Architecture

The project follows an MVC-inspired layered architecture:

- **Model Layer**: Data structures (AST nodes, diff results)
- **Controller Layer**: Business logic (parser, diff engine, matcher)
- **View Layer**: CLI interface and output formatting

## Documentation

- **[Findings](docs/findings.md)**: Research findings, limitations, and recommendations
- **[Normalization Model](docs/normalization_model.md)**: Normalization approach and rules
- **[API Reference](docs/api_reference.md)**: Complete API documentation
- **[Sample Outputs](docs/examples/sample_outputs.json)**: Example diff outputs

## Acceptance Criteria Status

- ✅ **AC1**: Parser evaluation documented in `docs/findings.md`
- ✅ **AC2**: Normalization model documented in `docs/normalization_model.md`
- ✅ **AC3**: All change types implemented (ADDED, DELETED, MODIFIED, MOVED, MOVED_AND_MODIFIED)
- ✅ **AC5**: Tested with 5+ sample files
- ✅ **AC6**: Limitations documented in `docs/findings.md`
- ✅ **AC7**: Sample outputs in `docs/examples/sample_outputs.json`
- ✅ **AC8**: Complete documentation provided

## Limitations

See [Findings](docs/findings.md) for detailed limitations. Key points:

- Duplicate key handling may need improvement
- Very large files (>10K properties) may have performance issues
- Comments are parsed but changes not fully tracked
- Encoding detection is basic (UTF-8 and ISO-8859-1 supported)

## Contributing

This is a POC project. For production use, consider:

1. Enhanced error handling
2. Performance optimization for large files
3. Better duplicate key handling
4. Comment change tracking
5. Visual diff output

## License

This is a proof-of-concept implementation for research purposes.

## Contact

For questions or issues, please refer to the project documentation or create an issue in the project repository.
