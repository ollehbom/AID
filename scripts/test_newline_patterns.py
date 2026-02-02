#!/usr/bin/env python3
"""
Test with the exact pattern from the error message.
"""

from json_fixer import _escape_newlines_in_string_values, fix_json_string
import json

# The error shows position at line 2 column 18 (char 19)
# That's right at the opening quote of the value
# This suggests maybe there's a BOM or invalid character before the quote
test_json1 = '''{
  "design_spec": "# Design Specification: Core React Application Shell (test-single-workflow-8)\\n\\n## 1. Overview\\n\\n'''

print("Test 1: Truncated JSON (no closing)")
print(repr(test_json1))
try:
    result = json.loads(test_json1)
    print("✓ Parsed")
except json.JSONDecodeError as e:
    print(f"✗ Error: {e}")
    print(f"  Position: {e.pos}, Line: {e.lineno}, Col: {e.colno}")

print("\n" + "="*80 + "\n")

# Maybe there's a quote issue?
test_json2 = '''{
  "design_spec": "# Design Specification: Core React Application Shell (test-single-workflow-8)"\\n\\n## 1. Overview\\n\\n'''

print("Test 2: Escaped quote outside string?")
print(repr(test_json2))
try:
    result = json.loads(test_json2)
    print("✓ Parsed")
except json.JSONDecodeError as e:
    print(f"✗ Error: {e}")
    print(f"  Position: {e.pos}, Line: {e.lineno}, Col: {e.colno}")

print("\n" + "="*80 + "\n")

# Or maybe gemini is returning something weird like escaped quotes in the key?
test_json3 = '''{
  "design_spec\": "# Design Specification'''

print("Test 3: Escaped quote in key name?")
print(repr(test_json3))
try:
    result = json.loads(test_json3)
    print("✓ Parsed")
except json.JSONDecodeError as e:
    print(f"✗ Error: {e}")
    print(f"  Position: {e.pos}, Line: {e.lineno}, Col: {e.colno}")

print("\n" + "="*80 + "\n")

# Check what fix_json_string returns for truncated JSON
test_json4 = '''{
  "design_spec": "# Design Specification with
actual newline here
and another"}'''

print("Test 4: Actual newlines in value")
print("Original:", repr(test_json4))
fixed, was_modified = fix_json_string(test_json4)
print("Fixed:", repr(fixed))
print("Was modified:", was_modified)
try:
    result = json.loads(fixed)
    print("✓ Parsed successfully!")
    print(result)
except json.JSONDecodeError as e:
    print(f"✗ Error: {e}")
    print(f"  Position: {e.pos}, Line: {e.lineno}, Col: {e.colno}")
