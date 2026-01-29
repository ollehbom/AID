#!/usr/bin/env python3
"""
Error Recovery Agent Executor
Analyzes pipeline errors and implements automatic fixes.
"""

import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MODEL = os.getenv("MODEL", "gpt-4.1")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
REPO_ROOT = Path(__file__).parent.parent
AGENT_FILE = REPO_ROOT / ".ai/agents/error-recovery.md"


def load_file(filepath):
    """Load content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[File not found: {filepath}]"


def save_file(filepath, content):
    """Save content to a file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def _invoke_openai(system_prompt, user_prompt):
    """Invoke OpenAI API."""
    import openai
    
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # Lower temperature for more deterministic fixes
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


def _invoke_gemini(system_prompt, user_prompt):
    """Invoke Google Gemini API."""
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_prompt,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    )
    
    response = model.generate_content(user_prompt)
    return response.text


def extract_error_from_issue(issue_body):
    """Extract error log from issue body."""
    # Look for error log section
    error_match = re.search(r'## Error Log\s+(.*?)(?=##|$)', issue_body, re.DOTALL)
    if error_match:
        return error_match.group(1).strip()
    return issue_body


def invoke_error_recovery_agent(error_id, issue_body):
    """
    Invoke the Error Recovery Agent to analyze and fix errors.
    
    Args:
        error_id: Unique identifier for this error
        issue_body: The GitHub issue body containing error details
    
    Returns:
        dict with analysis, fix details, and updates
    """
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    
    # Extract error log
    error_log = extract_error_from_issue(issue_body)
    
    # Construct the prompt
    system_prompt = f"""{agent_instructions}

You are now executing as the Error Recovery Agent in the AID pipeline.

Your task is to analyze the error and produce a structured fix according to your role.
Output MUST be valid JSON.
"""

    user_prompt = f"""# Error Recovery Task

## Error ID
{error_id}

## Error Log
{error_log}

## Repository Context
Repository Root: {REPO_ROOT}

---

## Your Task

1. Parse the error log to identify:
   - Error type
   - Affected file(s) and line number(s)
   - Root cause

2. Read the affected files using the context above

3. Determine the minimal fix required

4. Generate the complete fix including:
   - File modifications (with full new content)
   - Additional actions needed
   - Validation steps

5. Create documentation for the issue update

## Output Format

Provide your response in JSON format following the schema in your instructions.
Include all required keys: analysis, fix, validation, issue_update, pr_description
"""

    # Invoke AI API
    try:
        print(f"🤖 Analyzing error with {AI_PROVIDER.upper()} ({MODEL})...")
        
        if AI_PROVIDER == "gemini":
            result_json = _invoke_gemini(system_prompt, user_prompt)
        else:
            result_json = _invoke_openai(system_prompt, user_prompt)
        
        result = json.loads(result_json)
        
        # Save outputs
        output_dir = REPO_ROOT / ".ai" / "error-fixes"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save analysis
        save_file(output_dir / f"{error_id}-analysis.json", json.dumps(result, indent=2))
        
        # Save issue update
        if "issue_update" in result:
            save_file(output_dir / f"{error_id}-issue-update.md", result["issue_update"])
        
        # Save PR description
        if "pr_description" in result:
            save_file(output_dir / f"{error_id}-pr-description.md", result["pr_description"])
        
        # Apply file fixes
        if "fix" in result and "files_to_modify" in result["fix"]:
            for file_fix in result["fix"]["files_to_modify"]:
                file_path = REPO_ROOT / file_fix["path"]
                if "new_content" in file_fix:
                    print(f"✏️  Applying fix to {file_fix['path']}")
                    save_file(file_path, file_fix["new_content"])
        
        print("✅ Error analysis and fix complete!")
        print(f"\nError Type: {result['analysis']['error_type']}")
        print(f"Root Cause: {result['analysis']['root_cause']}")
        print(f"\nFixed Files:")
        for file_fix in result.get("fix", {}).get("files_to_modify", []):
            print(f"  - {file_fix['path']}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: AI response was not valid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during agent execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python invoke_error_recovery_agent.py <error_id> <issue_body_file>")
        sys.exit(1)
    
    error_id = sys.argv[1]
    issue_body_file = sys.argv[2]
    
    # Read issue body
    issue_body = load_file(issue_body_file)
    
    # Invoke agent
    result = invoke_error_recovery_agent(error_id, issue_body)
    
    # Exit successfully
    sys.exit(0)


if __name__ == "__main__":
    main()
