# Normalization Model

## Overview

The normalization model converts parsed AST nodes into a unified internal format for comparison. This ensures consistent diff detection regardless of formatting differences.

## Normalization Rules

### Key Normalization

Keys are normalized by:
- **Trimming whitespace**: Leading and trailing whitespace is removed
- **Preserving case**: Case is preserved (keys are case-sensitive)
- **No other transformations**: Special characters and structure are maintained

Example:
```
  key1  → key1
key2    → key2
```

### Value Normalization

Values are normalized by:
- **Trimming trailing whitespace**: Only trailing whitespace is removed
- **Preserving leading whitespace**: Leading whitespace is preserved (may be intentional)

Example:
```
value1  → value1
  value2  →   value2 (leading spaces preserved)
```

### Rationale

1. **Trailing Whitespace**: Typically unintentional and should be ignored for comparison
2. **Leading Whitespace**: May be intentional (e.g., indentation in multi-line values)
3. **Case Sensitivity**: Property keys are typically case-sensitive, so we preserve case

## Semantic Equivalence

Two values are considered semantically equivalent if they are equal after normalization:

```python
Normalizer.are_values_semantically_equivalent("value  ", "value")  # True
Normalizer.are_values_semantically_equivalent("value1", "value2")   # False
```

## AST Normalization

The entire AST is normalized by:
1. Normalizing all property nodes (keys and values)
2. Preserving line numbers (critical for move detection)
3. Preserving empty lines and comments (for structure)
4. Maintaining file path reference

## Use Cases

### Whitespace-Only Changes

Normalization allows detection of whitespace-only changes as semantically equivalent:

```
Source: key=value
Target: key=value  
```

### Formatting Differences

Handles minor formatting differences without false positives:

```
Source: key = value
Target: key=value
→ Both normalize to same key/value, detected correctly
```

## Future Enhancements

Potential normalization enhancements:
- Case-insensitive comparison option
- Unicode normalization (NFD vs NFC)
- Number format normalization (e.g., "1.0" vs "1")
- Date format normalization
- Boolean value normalization ("true" vs "True" vs "1")
