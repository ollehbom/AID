# JSON Fixer Utility

## Overview

The `json_fixer.py` utility provides automatic recovery for malformed JSON responses from AI models, particularly addressing common issues with Google Gemini models. This utility is used by all agent scripts in the AID pipeline.

## Problem Statement

AI models, especially Gemini, sometimes generate JSON with invalid control characters or formatting issues that cause parsing failures. Example errors:

- `Invalid control character at: line 3 column 354 (char 2859)`
- Unescaped newlines in string values
- Trailing commas in objects/arrays
- JSON wrapped in markdown code blocks

## Solution

The `json_fixer.py` module provides two main functions:

### `fix_json_string(json_string)`

Applies automatic fixes to common JSON issues:

1. Removes BOM (Byte Order Mark) characters
2. Strips whitespace
3. Extracts JSON from markdown code blocks
4. **Removes invalid control characters (ASCII 0-31)** - the most common issue
5. Fixes trailing comma issues
6. Removes trailing content after the main JSON object

Returns: `(fixed_json_string, was_modified)`

### `parse_json_with_recovery(json_string, save_error_file=True, error_prefix="json_parse_error")`

The main function used by all agent scripts. Attempts multiple recovery strategies:

1. **First attempt**: Apply automatic fixes via `fix_json_string()`
2. **Second attempt**: Aggressive recovery - truncate at error position and close JSON properly
3. **Third attempt**: Extract JSON from surrounding text
4. **If all fail**: Save detailed debug information and re-raise the error

Returns: Parsed JSON object (dict or list)

## Integration

All agent scripts have been updated to use this utility:

- `invoke_product_agent.py`
- `invoke_dev_agent.py`
- `invoke_dev_agent_iterative.py`
- `invoke_design_agent.py`
- `invoke_ops_agent.py`
- `invoke_error_recovery_agent.py`
- `invoke_architect_agent.py`

### Usage Example

```python
from json_fixer import parse_json_with_recovery

# In your agent script's API invocation function
response_text = model.generate_content(prompt)

# Instead of: json.loads(response_text)
# Use:
result = parse_json_with_recovery(
    response_text,
    error_prefix="my_agent_error"
)
```

## Features

### Automatic Fixes Applied

- ✅ Control character removal (fixes "Invalid control character" errors)
- ✅ BOM character removal
- ✅ Markdown code block extraction
- ✅ Trailing comma removal
- ✅ Trailing content truncation

### Recovery Strategies

- ✅ Truncate at error position and close JSON properly
- ✅ Remove incomplete strings at the end
- ✅ Balance brackets and braces
- ✅ Extract JSON from surrounding text
- ✅ Add `_recovery_note` field when partial recovery succeeds

### Debug Support

When all recovery attempts fail:

- Saves original JSON string to file
- Saves fixed (but still unparsable) JSON string
- Saves error details (message, position, line, column)
- Shows context around error position with marker
- Provides brief console output with error location

## Test Results

The utility successfully handles:

- ✅ Control characters in strings (`\x01`, `\x08`, etc.)
- ✅ JSON wrapped in markdown code blocks
- ✅ Trailing commas in objects and arrays
- ⚠️ Incomplete JSON (partial recovery where possible)

## Performance Impact

- Minimal overhead for valid JSON
- Adds 2-3 additional parsing attempts only when initial parse fails
- File I/O only occurs when all recovery attempts fail

## Benefits

1. **Reduces pipeline failures** from AI-generated JSON errors
2. **Automatic recovery** without manual intervention
3. **Comprehensive debugging** when recovery fails
4. **Centralized solution** used by all agent scripts
5. **Graceful degradation** with partial recovery support

## Future Enhancements

Potential improvements:

- Support for escaped unicode sequences
- More sophisticated string value escaping
- Configurable recovery strategies
- Statistics/telemetry on recovery success rates
