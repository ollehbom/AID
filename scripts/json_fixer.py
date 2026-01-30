#!/usr/bin/env python3
"""
JSON Fixer Utility
Automatically fixes common JSON errors from AI model outputs, especially Gemini models.
Can be imported and used by all agent scripts.
"""

import json
import re
import sys
from datetime import datetime


def fix_json_string(json_string):
    """
    Attempt to fix common JSON errors in AI-generated content.
    
    Args:
        json_string: The potentially malformed JSON string
        
    Returns:
        tuple: (fixed_json_string, was_modified)
        
    Raises:
        ValueError: If the JSON cannot be fixed
    """
    original = json_string
    modified = False
    
    # 1. Remove BOM (Byte Order Mark) if present
    if json_string.startswith('\ufeff'):
        json_string = json_string[1:]
        modified = True
    
    # 2. Strip whitespace
    json_string = json_string.strip()
    
    # 3. Extract JSON from markdown code blocks if wrapped
    if json_string.startswith("```"):
        lines = json_string.split('\n')
        # Remove first line (```json or ```) and last line (```)
        if len(lines) > 2:
            json_string = '\n'.join(lines[1:-1])
            modified = True
    
    # 4. Remove invalid control characters (ASCII 0-31 except tab, newline, carriage return)
    # These are the most common issues from Gemini models
    control_char_pattern = r'[\x00-\x08\x0b\x0c\x0e-\x1f]'
    if re.search(control_char_pattern, json_string):
        json_string = re.sub(control_char_pattern, '', json_string)
        modified = True
    
    # 5. Fix common escape sequence issues
    # Replace unescaped newlines in strings (but not actual JSON structure newlines)
    # This is tricky - we need to find strings and escape newlines within them
    def escape_newlines_in_strings(match):
        """Escape newlines within a JSON string value."""
        string_content = match.group(1)
        # Replace actual newlines with \n
        string_content = string_content.replace('\n', '\\n')
        string_content = string_content.replace('\r', '\\r')
        string_content = string_content.replace('\t', '\\t')
        return f'"{string_content}"'
    
    # This regex tries to match string values, avoiding already-escaped quotes
    # It's not perfect but handles many cases
    try:
        # More conservative approach - only fix obvious issues
        json_string = json_string.replace('\\\n', '\\n')  # Fix double-escaped newlines
    except Exception:
        pass  # If any replacement fails, continue with original
    
    # 6. Fix common trailing comma issues
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
    
    # 7. Remove any trailing content after the main JSON object/array
    # Find the matching closing brace/bracket for the opening one
    if json_string.startswith('{'):
        # Count braces to find where the object truly ends
        brace_count = 0
        for i, char in enumerate(json_string):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    if i < len(json_string) - 1:
                        json_string = json_string[:i+1]
                        modified = True
                    break
    elif json_string.startswith('['):
        bracket_count = 0
        for i, char in enumerate(json_string):
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    if i < len(json_string) - 1:
                        json_string = json_string[:i+1]
                        modified = True
                    break
    
    return json_string, (modified or json_string != original)


def parse_json_with_recovery(json_string, save_error_file=True, error_prefix="json_parse_error"):
    """
    Parse JSON with automatic error recovery.
    
    Attempts multiple strategies to fix and parse malformed JSON:
    1. Fix common issues (control characters, formatting)
    2. If that fails, try to recover partial JSON by truncating at error position
    3. Save debug information if all attempts fail
    
    Args:
        json_string: The JSON string to parse
        save_error_file: Whether to save error details to a file
        error_prefix: Prefix for error file name
        
    Returns:
        dict or list: The parsed JSON object
        
    Raises:
        json.JSONDecodeError: If JSON cannot be parsed or recovered
    """
    original_string = json_string
    
    # First attempt: Fix common issues
    try:
        fixed_string, was_fixed = fix_json_string(json_string)
        if was_fixed:
            print(f"✓ Applied automatic JSON fixes", file=sys.stderr)
        result = json.loads(fixed_string)
        return result
    except json.JSONDecodeError as e:
        print(f"⚠ JSON parsing failed after auto-fix: {e}", file=sys.stderr)
        first_error = e
    
    # Second attempt: Try to fix missing comma/delimiter issues
    if "delimiter" in str(first_error).lower() or "expecting ','" in str(first_error).lower():
        print(f"Attempting to fix missing delimiter...", file=sys.stderr)
        try:
            fixed_string, _ = fix_json_string(json_string)
            comma_fixed = _fix_missing_commas(fixed_string, first_error)
            if comma_fixed:
                result = json.loads(comma_fixed)
                print(f"✓ Fixed missing delimiter issue", file=sys.stderr)
                return result
        except Exception as comma_error:
            print(f"Comma fix failed: {comma_error}", file=sys.stderr)
    
    # Third attempt: Try to fix unterminated string issues
    if "unterminated string" in str(first_error).lower():
        print(f"Attempting to fix unterminated string...", file=sys.stderr)
        try:
            fixed_string, _ = fix_json_string(json_string)
            string_fixed = _fix_unterminated_string(fixed_string, first_error)
            if string_fixed:
                result = json.loads(string_fixed)
                print(f"✓ Fixed unterminated string issue", file=sys.stderr)
                return result
        except Exception as string_error:
            print(f"String fix failed: {string_error}", file=sys.stderr)
    
    # Fourth attempt: Aggressive recovery - truncate and close
    print(f"Attempting aggressive JSON recovery...", file=sys.stderr)
    try:
        fixed_string, _ = fix_json_string(json_string)
        recovered = _truncate_and_close_json(fixed_string, first_error)
        if recovered:
            print(f"✓ Recovered partial JSON with {len(recovered)} top-level fields", file=sys.stderr)
            recovered["_recovery_note"] = (
                f"JSON was truncated due to parsing error at position {first_error.pos}. "
                f"Some fields may be incomplete or missing."
            )
            return recovered
    except Exception as recovery_error:
        print(f"Aggressive recovery failed: {recovery_error}", file=sys.stderr)
    
    # Fifth attempt: Try to extract JSON from possible surrounding text
    try:
        print(f"Attempting to extract JSON from surrounding text...", file=sys.stderr)
        extracted = _extract_json_from_text(original_string)
        if extracted:
            result = json.loads(extracted)
            print(f"✓ Successfully extracted and parsed JSON from text", file=sys.stderr)
            return result
    except Exception as extract_error:
        print(f"Extraction attempt failed: {extract_error}", file=sys.stderr)
    
    # All attempts failed - save debug info and raise
    if save_error_file:
        error_file = f"{error_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Original JSON String:\n")
                f.write("="*80 + "\n")
                f.write(original_string)
                f.write("\n\n" + "="*80 + "\n")
                f.write(f"Fixed JSON String:\n")
                f.write("="*80 + "\n")
                fixed_string, _ = fix_json_string(original_string)
                f.write(fixed_string)
                f.write("\n\n" + "="*80 + "\n")
                f.write(f"Error Details:\n")
                f.write(f"  Message: {first_error.msg}\n")
                f.write(f"  Position: {first_error.pos}\n")
                f.write(f"  Line: {first_error.lineno}, Column: {first_error.colno}\n")
                
                # Write context around error
                if first_error.pos:
                    start = max(0, first_error.pos - 300)
                    end = min(len(fixed_string), first_error.pos + 300)
                    f.write(f"\nContext around error (position {first_error.pos}):\n")
                    f.write("="*80 + "\n")
                    context = fixed_string[start:end]
                    # Mark the error position
                    error_offset = first_error.pos - start
                    f.write(context[:error_offset])
                    f.write("<<<ERROR HERE>>>")
                    f.write(context[error_offset:])
                    f.write("\n")
            
            print(f"\n✗ Failed to parse JSON. Full response saved to {error_file}", file=sys.stderr)
            print(f"  Error: {first_error}", file=sys.stderr)
            
            # Show brief context
            if first_error.pos:
                start = max(0, first_error.pos - 100)
                end = min(len(fixed_string), first_error.pos + 100)
                print(f"\n  Context: ...{fixed_string[start:end]}...", file=sys.stderr)
        except Exception as save_error:
            print(f"Warning: Could not save error file: {save_error}", file=sys.stderr)
    
    # Re-raise the original error
    raise first_error


def _fix_missing_commas(json_string, error):
    """
    Attempt to fix missing comma/delimiter errors.
    
    Common issues:
    - Missing comma between object properties
    - Missing comma between array elements
    - Extra/missing quotes causing delimiter confusion
    
    Args:
        json_string: The JSON string with a delimiter error
        error: The JSONDecodeError exception
        
    Returns:
        str or None: Fixed JSON string or None if fix failed
    """
    if not hasattr(error, 'pos') or not error.pos:
        return None
    
    # Get context around the error
    pos = error.pos
    start = max(0, pos - 100)
    end = min(len(json_string), pos + 100)
    context = json_string[start:end]
    
    # Try multiple comma fix strategies
    attempts = []
    
    # Strategy 1: Insert comma before the error position
    # Common case: }{ or ][ without comma
    if pos > 0:
        before_char = json_string[pos-1:pos]
        at_char = json_string[pos:pos+1]
        
        # Look back further to handle whitespace
        # Find the last non-whitespace character before position
        look_back = pos - 1
        while look_back >= 0 and json_string[look_back] in ' \t\n\r':
            look_back -= 1
        
        if look_back >= 0:
            last_nonwhite = json_string[look_back]
            
            # Case: }{"key" or ]{"key" or } "key" - missing comma after } or ]
            if last_nonwhite in ['}', ']'] and at_char in ['{', '"']:
                # Insert comma after the last non-whitespace char, before current pos
                attempt = json_string[:look_back+1] + ',' + json_string[look_back+1:]
                attempts.append(("Insert comma after } or ]", attempt))
            
            # Case: "value" "key" - missing comma between string values
            if last_nonwhite == '"' and at_char == '"':
                attempt = json_string[:look_back+1] + ',' + json_string[look_back+1:]
                attempts.append(("Insert comma between string properties", attempt))
            
            # Case: number "key" or boolean "key" - missing comma after value
            if last_nonwhite.isdigit() and at_char == '"':
                attempt = json_string[:look_back+1] + ',' + json_string[look_back+1:]
                attempts.append(("Insert comma after numeric value", attempt))
        
        # Direct character comparison (no whitespace)
        # Case: "value"{"key" - missing comma after closing quote
        if before_char == '"' and at_char in ['{', '"']:
            attempt = json_string[:pos] + ',' + json_string[pos:]
            attempts.append(("Insert comma directly after quote", attempt))
    
    # Strategy 2: Look for common patterns like }} or ]] that might need comma
    # Search backwards from error position for property boundaries
    if pos > 10:
        # Find the last complete property before error
        search_start = max(0, pos - 500)
        substring = json_string[search_start:pos]
        
        # Look for patterns like: "value"\n\s*"key" (missing comma)
        pattern = r'(["\]}])(\s+)(["\[{])'
        matches = list(re.finditer(pattern, substring))
        
        if matches:
            # Take the last match (closest to error)
            last_match = matches[-1]
            # Calculate absolute position
            abs_pos = search_start + last_match.start() + len(last_match.group(1))
            attempt = json_string[:abs_pos] + ',' + json_string[abs_pos:]
            attempts.append(("Insert comma between elements (pattern match)", attempt))
    
    # Strategy 3: Try removing extra characters around the error position
    # Sometimes there's a stray character causing issues
    if pos > 0 and pos < len(json_string):
        # Try removing character at error position
        attempt = json_string[:pos] + json_string[pos+1:]
        attempts.append(("Remove character at error position", attempt))
        
        # Try removing character before error position
        attempt = json_string[:pos-1] + json_string[pos:]
        attempts.append(("Remove character before error position", attempt))
    
    # Try each attempt
    for strategy, attempt in attempts:
        try:
            json.loads(attempt)
            print(f"✓ Fixed using: {strategy}", file=sys.stderr)
            return attempt
        except:
            continue
    
    return None


def _fix_unterminated_string(json_string, error):
    """
    Attempt to fix unterminated string errors.
    
    Common causes:
    - Unescaped quotes within string values
    - Unescaped backslashes before quotes
    - Nested JSON strings that aren't properly escaped
    - Missing closing quote
    
    Args:
        json_string: The JSON string with an unterminated string error
        error: The JSONDecodeError exception
        
    Returns:
        str or None: Fixed JSON string or None if fix failed
    """
    if not hasattr(error, 'pos') or not error.pos:
        return None
    
    pos = error.pos
    attempts = []
    
    # Strategy 1: Look backwards from error position to find the opening quote
    # Then look forward to find unescaped quotes and escape them
    if pos > 10:
        # Find the start of the string (opening quote)
        string_start = None
        for i in range(pos - 1, max(0, pos - 1000), -1):
            if json_string[i] == '"':
                # Check if this quote is escaped
                num_backslashes = 0
                j = i - 1
                while j >= 0 and json_string[j] == '\\':
                    num_backslashes += 1
                    j -= 1
                # If even number of backslashes (including 0), the quote is not escaped
                if num_backslashes % 2 == 0:
                    string_start = i
                    break
        
        if string_start is not None:
            # Strategy 1a: Find and escape unescaped quotes within the string
            # Look forward from string_start to find the problematic quote
            attempt = list(json_string)
            search_pos = string_start + 1
            while search_pos < len(json_string):
                if json_string[search_pos] == '"':
                    # Check if escaped
                    num_backslashes = 0
                    j = search_pos - 1
                    while j >= 0 and json_string[j] == '\\':
                        num_backslashes += 1
                        j -= 1
                    
                    # If not escaped and we're still in a string context
                    if num_backslashes % 2 == 0:
                        # Check if this might be a legitimate end quote
                        # Look at what comes after: should be comma, brace, bracket, or whitespace
                        next_non_space = search_pos + 1
                        while next_non_space < len(json_string) and json_string[next_non_space] in ' \t\n\r':
                            next_non_space += 1
                        
                        if next_non_space < len(json_string):
                            next_char = json_string[next_non_space]
                            # If it's not a valid JSON separator, this quote should be escaped
                            if next_char not in [',', '}', ']', ':']:
                                # Escape this quote
                                attempt[search_pos] = '\\"'
                                fixed_attempt = ''.join(attempt)
                                attempts.append(("Escape unescaped quote in string", fixed_attempt))
                                break
                        
                        # Otherwise this might be the legitimate end, stop here
                        break
                
                search_pos += 1
            
            # Strategy 1b: Close the string at the error position
            # Add a closing quote at the error position
            if pos < len(json_string):
                # Insert closing quote and continue
                attempt = json_string[:pos] + '"' + json_string[pos:]
                attempts.append(("Close string at error position", attempt))
            
            # Strategy 1c: Look for the next quote after error and assume that's the real end
            # Remove content between error and next quote
            next_quote = json_string.find('"', pos)
            if next_quote != -1 and next_quote - pos < 200:  # Don't look too far
                # Keep content up to error, then skip to the quote
                attempt = json_string[:pos] + json_string[next_quote:]
                attempts.append(("Skip to next quote", attempt))
    
    # Strategy 2: If the string contains nested JSON (common pattern)
    # Try to properly escape the nested JSON
    if pos > 50:
        context_start = max(0, pos - 200)
        context = json_string[context_start:pos + 200]
        
        # Look for patterns like: "wireframe_json_string": "{...
        # This suggests nested JSON that needs escaping
        if '": "{"' in context or '": "{' in context:
            # Find the key that has nested JSON
            key_match = re.search(r'"([^"]+)":\s*"(\{[^"]*)$', json_string[:pos])
            if key_match:
                # Try to find the end of this nested JSON
                # Look for the closing brace pattern
                nested_start = key_match.start(2)
                # Find matching closing brace
                brace_count = 1
                search_pos = nested_start + 1
                nested_end = None
                
                while search_pos < len(json_string) and brace_count > 0:
                    if json_string[search_pos] == '{':
                        brace_count += 1
                    elif json_string[search_pos] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            nested_end = search_pos
                            break
                    search_pos += 1
                
                if nested_end:
                    # Extract the nested JSON
                    nested_json = json_string[nested_start:nested_end + 1]
                    # Escape it properly
                    escaped_nested = nested_json.replace('\\', '\\\\').replace('"', '\\"')
                    # Reconstruct
                    attempt = json_string[:nested_start] + escaped_nested + '"' + json_string[nested_end + 1:]
                    attempts.append(("Escape nested JSON string", attempt))
    
    # Try each attempt
    for strategy, attempt in attempts:
        try:
            json.loads(attempt)
            print(f"✓ Fixed using: {strategy}", file=sys.stderr)
            return attempt
        except:
            continue
    
    return None


def _truncate_and_close_json(json_string, error):
    """
    Attempt to recover JSON by truncating at error position and closing properly.
    
    Args:
        json_string: The JSON string with an error
        error: The JSONDecodeError exception
        
    Returns:
        dict or None: Recovered JSON object or None if recovery failed
    """
    if not hasattr(error, 'pos') or not error.pos:
        return None
    
    # Truncate at error position
    truncated = json_string[:error.pos]
    
    # Find the last complete key-value pair or array element
    # Look for the last comma, opening brace, or opening bracket
    last_comma = truncated.rfind(',')
    last_brace = truncated.rfind('{')
    last_bracket = truncated.rfind('[')
    
    # Truncate to last comma if it comes after the last opening
    if last_comma > max(last_brace, last_bracket):
        truncated = truncated[:last_comma]
    
    # Remove any incomplete string at the end
    # If we're in the middle of a string, remove it
    in_string = False
    escape_next = False
    last_complete = len(truncated)
    
    for i in range(len(truncated) - 1, -1, -1):
        char = truncated[i]
        if not escape_next and char == '"':
            if not in_string:
                in_string = True
            else:
                last_complete = i + 1
                break
        elif char == '\\':
            escape_next = not escape_next
        else:
            escape_next = False
    
    if in_string:
        truncated = truncated[:i]  # Remove incomplete string
    
    truncated = truncated.rstrip()
    
    # Count open brackets/braces and close them properly
    open_braces = truncated.count('{') - truncated.count('}')
    open_brackets = truncated.count('[') - truncated.count(']')
    
    # Remove trailing comma if present
    if truncated.endswith(','):
        truncated = truncated[:-1].rstrip()
    
    # Close all open structures
    for _ in range(open_brackets):
        truncated += "]"
    for _ in range(open_braces):
        truncated += "}"
    
    try:
        return json.loads(truncated)
    except:
        return None


def _extract_json_from_text(text):
    """
    Try to extract JSON object or array from surrounding text.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        str or None: Extracted JSON string or None if not found
    """
    # Look for JSON object
    obj_match = re.search(r'\{.*\}', text, re.DOTALL)
    if obj_match:
        return obj_match.group(0)
    
    # Look for JSON array
    arr_match = re.search(r'\[.*\]', text, re.DOTALL)
    if arr_match:
        return arr_match.group(0)
    
    return None


# Example usage
if __name__ == "__main__":
    # Test with some problematic JSON examples
    test_cases = [
        # Control character in string
        ('{"name": "test\x01value", "count": 42}', 'Control characters'),
        # Markdown wrapped
        ('```json\n{"key": "value"}\n```', 'Markdown wrapped'),
        # Trailing comma
        ('{"a": 1, "b": 2,}', 'Trailing comma'),
        # Missing comma between properties
        ('{"key1": "value1" "key2": "value2"}', 'Missing comma'),
        # Unterminated string with unescaped quote
        ('{"text": "Hello "world", "count": 42}', 'Unterminated string (unescaped quote)'),
        # Unterminated string - missing closing quote
        ('{"text": "Hello world, "count": 42}', 'Unterminated string (missing quote)'),
        # Nested JSON string (like wireframe scenario)
        ('{"data": "{\\"nested\\": \\"value\\"}", "other": "test"}', 'Nested JSON (properly escaped)'),
        # Incomplete JSON (expected to fail)
        ('{"complete": true, "incomplete": "val', 'Incomplete JSON (expected fail)'),
    ]
    
    passed = 0
    failed = 0
    
    for i, (test, description) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {description}")
        print(f"Input: {repr(test[:60])}{'...' if len(test) > 60 else ''}")
        try:
            result = parse_json_with_recovery(test, save_error_file=False)
            print(f"✓ Success: {result}")
            passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"{'='*60}")
