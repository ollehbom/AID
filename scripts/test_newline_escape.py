#!/usr/bin/env python3
"""
Test the newline escaping function with a problematic JSON string.
"""

from json_fixer import _escape_newlines_in_string_values
import json

# Simulate what Gemini might return (based on the error message)
test_json = '''{
  "design_spec": "# Design Specification: Core React Application Shell
## 1. Overview
This is a test with actual newlines in the string"
}'''

print("Original JSON:")
print(repr(test_json))
print("\n" + "="*80 + "\n")

print("After escaping:")
escaped = _escape_newlines_in_string_values(test_json)
print(repr(escaped))
print("\n" + "="*80 + "\n")

print("Attempting to parse:")
try:
    result = json.loads(escaped)
    print("✓ SUCCESS!")
    print(result)
except json.JSONDecodeError as e:
    print(f"✗ FAILED: {e}")
    print(f"Error at position {e.pos}, line {e.lineno}, col {e.colno}")
    if e.pos:
        start = max(0, e.pos - 50)
        end = min(len(escaped), e.pos + 50)
        print(f"\nContext: ...{escaped[start:end]}...")
