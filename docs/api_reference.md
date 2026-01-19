# API Reference

## Overview

This document provides API reference for the AST Diff POC library.

## Core Classes

### PropertyParser

Parser for Java-style `.properties` files.

#### Methods

##### `parse_file(file_path: str) -> PropertyFileAST`

Parse a property file from disk.

**Parameters:**
- `file_path`: Path to the property file

**Returns:**
- `PropertyFileAST`: Parsed AST representation

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If file cannot be parsed

##### `parse_string(content: str, file_path: Optional[str] = None) -> PropertyFileAST`

Parse a property file from a string.

**Parameters:**
- `content`: Content of the property file
- `file_path`: Optional path for reference

**Returns:**
- `PropertyFileAST`: Parsed AST representation

### DiffEngine

Engine for computing structural differences between property files.

#### Methods

##### `compute_diff(source_ast: PropertyFileAST, target_ast: PropertyFileAST) -> DiffResult`

Compute the diff between two ASTs.

**Parameters:**
- `source_ast`: Source file AST
- `target_ast`: Target file AST

**Returns:**
- `DiffResult`: Complete diff result with all changes

### Normalizer

Normalizes AST nodes for comparison.

#### Static Methods

##### `normalize_ast(ast: PropertyFileAST) -> PropertyFileAST`

Normalize an AST to canonical form.

##### `normalize_key(key: str) -> str`

Normalize a property key.

##### `normalize_value(value: str) -> str`

Normalize a property value.

##### `are_values_semantically_equivalent(value1: str, value2: str) -> bool`

Check if two values are semantically equivalent.

## Data Models

### PropertyNode

Represents a single property key-value pair.

**Attributes:**
- `line_number`: Line number (1-indexed)
- `key`: Property key
- `value`: Property value
- `raw_line`: Original line content
- `leading_whitespace`: Whitespace before key
- `separator`: Separator used (= or :)
- `trailing_whitespace_before_value`: Whitespace after separator
- `trailing_whitespace_after_value`: Whitespace after value

### PropertyFileAST

Container for all nodes in a property file.

**Attributes:**
- `nodes`: List of PropertyNode objects
- `empty_lines`: List of EmptyLineNode objects
- `comments`: List of CommentNode objects
- `file_path`: Optional file path

### DiffResult

Complete diff result.

**Attributes:**
- `source_file`: Path to source file
- `target_file`: Path to target file
- `changes`: List of DiffChange objects
- `summary`: DiffSummary object

**Methods:**
- `to_dict() -> dict`: Convert to dictionary for JSON serialization
- `calculate_summary() -> None`: Calculate summary statistics

### DiffChange

Represents a single change.

**Attributes:**
- `change_type`: ChangeType enum value
- `key`: Property key
- `source_line`: Line number in source (None for ADDED)
- `target_line`: Line number in target (None for DELETED)
- `source_value`: Value in source file
- `target_value`: Value in target file

### ChangeType

Enumeration of change types:
- `ADDED`: New property added
- `DELETED`: Property removed
- `MODIFIED`: Value changed, same line
- `MOVED`: Same key/value, different line
- `MOVED_AND_MODIFIED`: Value changed and moved

## Utility Functions

### `load_property_file(file_path: str) -> PropertyFileAST`

Load and parse a property file.

**Parameters:**
- `file_path`: Path to the property file

**Returns:**
- `PropertyFileAST`: Parsed AST

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If file cannot be parsed

## CLI Interface

### Command: `ast-diff`

Compute AST-based diff between two property files.

**Usage:**
```bash
ast-diff SOURCE_FILE TARGET_FILE [OPTIONS]
```

**Options:**
- `--output, -o`: Output file path (default: stdout)
- `--no-normalize`: Disable AST normalization
- `--pretty`: Pretty-print JSON output

**Example:**
```bash
ast-diff source.properties target.properties --output diff.json --pretty
```
