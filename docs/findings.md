# AST Diff POC - Research Findings

## Executive Summary

This document outlines the research findings, implementation approach, limitations, and recommendations for the AST-based diff POC for Property files.

## Parser Evaluation (AC1)

### Parser Choice: Custom Parser

After evaluating various options for parsing Java-style `.properties` files, we chose to implement a **custom parser** for the following reasons:

1. **Full Control**: Custom parser provides complete control over AST structure and metadata preservation
2. **Line Number Tracking**: Essential for accurate move detection and reporting
3. **Whitespace Preservation**: Maintains original formatting for semantic equivalence detection
4. **Flexibility**: Can handle edge cases and custom requirements specific to our use case

### Alternative Options Considered

- **configparser (Python stdlib)**: Limited support for Java-style properties, doesn't preserve line numbers
- **javaproperties library**: Better Java compatibility but still lacks fine-grained line tracking
- **Existing AST libraries**: Too generic, don't provide property-file-specific features

### Parser Capabilities

The custom parser supports:
- Standard key-value pairs (`key=value` and `key:value`)
- Escaped characters (`\n`, `\t`, `\uXXXX`, etc.)
- Unicode characters
- Empty lines (preserved for structure)
- Comments (basic support with `#` and `!`)
- Line continuation (backslash at end of line)
- Whitespace preservation around separators

### Parser Limitations

1. **Comments**: Comments are parsed but not fully integrated into diff logic
2. **Multi-line Values**: Line continuation is supported but complex multi-line values may need refinement
3. **Encoding**: Currently supports UTF-8 and ISO-8859-1, may need extension for other encodings
4. **Malformed Files**: Basic error handling, may need more robust recovery for edge cases

## Normalization Model (AC2)

See `normalization_model.md` for detailed documentation.

## Change Detection (AC3)

The diff engine successfully detects all required change types:

- ✅ **Additions**: New keys in target file
- ✅ **Deletions**: Keys removed from source file
- ✅ **Modifications**: Same key, different value, same line
- ✅ **Moves**: Same key and value, different line numbers
- ✅ **Moved and Modified**: Same key, different value, different line numbers
- ✅ **Semantic Equivalence**: Detected through normalization (whitespace-only differences)

## Test Results (AC5)

The POC has been tested with 5 sample property file pairs, covering various scenarios:

- Sample 1: Simple moves and modifications
- Sample 2: Additions, deletions, and value changes
- Sample 3: Complex reordering and modifications
- Sample 4: Large file with multiple change types
- Sample 5: Configuration file with extensive changes

All samples demonstrate accurate detection of structural changes.

## Limitations and Gaps (AC6)

### Current Limitations

1. **Duplicate Keys**: When the same key appears multiple times, matching may not be perfect. The matcher uses position-based heuristics but could be improved.

2. **Move Detection Accuracy**: For files with many similar keys, move detection may occasionally misclassify changes as separate add/delete rather than moves.

3. **Semantic Equivalence**: Currently only handles whitespace normalization. More sophisticated semantic analysis (e.g., case-insensitive comparison) could be added.

4. **Performance**: For very large files (10,000+ properties), performance may degrade. Optimization opportunities exist.

5. **Comment Handling**: Comments are parsed but changes to comments are not tracked in the diff.

6. **Empty Line Significance**: Empty lines are tracked but their role in diff results is minimal.

### Parser Restrictions

1. **Strict Format**: Requires standard Java properties format. Non-standard variations may not parse correctly.

2. **Escaping**: Complex escape sequences may not be fully supported (e.g., nested escapes).

3. **Encoding Detection**: Automatic encoding detection is not implemented; relies on fallback mechanism.

4. **Large Files**: Very large files (>1MB) may have performance issues.

## Recommendations for Implementation

### Short-term Improvements

1. **Enhanced Matching**: Improve duplicate key handling with better context-aware matching
2. **Performance Optimization**: Add caching and optimize for large files
3. **Better Error Messages**: More descriptive error messages for malformed files
4. **Comment Diff**: Add support for tracking comment changes

### Long-term Enhancements

1. **Incremental Diff**: Support for diffing against previous versions incrementally
2. **Merge Support**: Three-way merge capabilities
3. **Conflict Detection**: Identify and report merge conflicts
4. **Visualization**: HTML/visual diff output for better human readability
5. **Batch Processing**: Optimize for processing multiple file pairs efficiently

### Production Readiness Checklist

- [ ] Comprehensive error handling and recovery
- [ ] Performance testing with large files (10K+ properties)
- [ ] Memory optimization for large ASTs
- [ ] Logging and monitoring integration
- [ ] API documentation and examples
- [ ] Integration tests with real-world property files
- [ ] Security review (file path validation, etc.)

## Conclusion

The AST-based diff POC successfully demonstrates the feasibility of structural diff detection for property files. The custom parser approach provides the necessary control and accuracy for production use, with identified limitations that can be addressed in future iterations.
