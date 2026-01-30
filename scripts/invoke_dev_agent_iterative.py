#!/usr/bin/env python3
"""
Dev Agent Executor - Iterative Approach
Invokes the Dev Agent in multiple iterations to avoid large JSON responses.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MODEL = os.getenv("MODEL", "gpt-4.1")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
REPO_ROOT = Path(__file__).parent.parent
AGENT_FILE = REPO_ROOT / ".ai/agents/dev.md"


def load_file(filepath):
    """Load content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[File not found: {filepath}]"


def save_file(filepath, content):
    """Save content to a file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def invoke_dev_agent_iterative(feature_id):
    """
    Invoke the Dev Agent in iterations to avoid large JSON responses.
    
    Args:
        feature_id: Identifier for this feature
        
    Returns:
        dict: Combined results from all iterations
    """
    print("🔄 Invoking Dev Agent with iterative workflow...")
    
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    if agent_instructions.startswith("[File not found"):
        agent_instructions = """You are an expert software engineering agent."""
    
    # Load technical specifications
    adr_files = list((REPO_ROOT / "design/architecture").glob(f"ADR-*-{feature_id}.md"))
    technical_spec_file = REPO_ROOT / "design/technical-specs" / f"{feature_id}.md"
    design_spec_file = REPO_ROOT / "design/specs" / f"{feature_id}.md"
    
    adrs = "\n\n---\n\n".join([load_file(adr) for adr in adr_files]) if adr_files else "[No ADRs found]"
    technical_spec = load_file(technical_spec_file)
    design_spec = load_file(design_spec_file)
    
    # Define iterations - each generates fewer files
    iterations = [
        {
            "name": "Project Configuration",
            "focus": "package.json, tsconfig.json, vite.config.js, .gitignore",
            "max_files": 5
        },
        {
            "name": "Core Implementation Files",
            "focus": "Main application code, components, utilities",
            "max_files": 5
        },
        {
            "name": "Additional Implementation",
            "focus": "Remaining implementation files if needed",
            "max_files": 5
        },
        {
            "name": "Test Files",
            "focus": "Test files for the implementation",
            "max_files": 5
        },
        {
            "name": "Documentation",
            "focus": "README.md and other documentation",
            "max_files": 3
        }
    ]
    
    combined_result = {
        "implementation_summary": "",
        "files_created": [],
        "tests_created": [],
        "documentation_updates": [],
        "quality_checklist": {},
        "technical_debt": [],
        "next_steps": ""
    }
    
    # Track what's been generated
    generated_files = []
    
    # Execute each iteration
    for i, iteration in enumerate(iterations, 1):
        print(f"\n📦 Iteration {i}/{len(iterations)}: {iteration['name']}")
        print(f"   Focus: {iteration['focus']}")
        print(f"   Max files: {iteration['max_files']}")
        
        try:
            result = _invoke_iteration(
                agent_instructions,
                adrs,
                technical_spec,
                design_spec,
                feature_id,
                iteration,
                generated_files,
                i,
                len(iterations)
            )
            
            # Track generated files
            for file_info in result.get("files_created", []):
                generated_files.append(file_info["path"])
            
            # Merge results
            if i == 1:
                combined_result["implementation_summary"] = result.get("implementation_summary", "")
            else:
                summary = result.get("implementation_summary", "")
                if summary:
                    combined_result["implementation_summary"] += f"\n\n### Iteration {i}: {iteration['name']}\n{summary}"
            
            combined_result["files_created"].extend(result.get("files_created", []))
            combined_result["tests_created"].extend(result.get("tests_created", []))
            combined_result["documentation_updates"].extend(result.get("documentation_updates", []))
            
            # Update checklist and debt from last iteration
            if result.get("quality_checklist"):
                combined_result["quality_checklist"] = result["quality_checklist"]
            if result.get("technical_debt"):
                combined_result["technical_debt"].extend(result["technical_debt"])
            if result.get("next_steps"):
                combined_result["next_steps"] = result["next_steps"]
            
            files_count = len(result.get("files_created", []))
            print(f"   ✓ Generated {files_count} files")
            
            # If no files generated, skip remaining iterations of same type
            if files_count == 0 and i > 2:
                print(f"   → Skipping remaining iterations (no more files needed)")
                break
            
        except Exception as e:
            print(f"   ⚠️  Iteration {i} failed: {e}")
            print(f"   Continuing with remaining iterations...")
            continue
    
    print(f"\n📊 Total files generated: {len(combined_result['files_created'])} implementation, {len(combined_result['tests_created'])} tests")
    
    return combined_result


def _invoke_iteration(agent_instructions, adrs, technical_spec, design_spec, 
                     feature_id, iteration, generated_files, iteration_num, total_iterations):
    """Execute a single iteration of dev work."""
    
    generated_list = "\n".join([f"- {f}" for f in generated_files]) if generated_files else "None yet"
    
    system_prompt = f"""{agent_instructions}

You are the Dev Agent in iteration {iteration_num} of {total_iterations}.

## THIS ITERATION: {iteration['name']}

**Focus**: {iteration['focus']}
**Max Files**: Generate UP TO {iteration['max_files']} files (can be fewer)

## Files Already Generated
{generated_list}

## Rules for This Iteration
1. Generate ONLY files matching this iteration's focus
2. Do NOT regenerate files already created
3. Maximum {iteration['max_files']} files
4. If no more files needed for this focus, return empty arrays
5. Keep each file concise but complete
6. Properly escape ALL special characters in JSON
"""

    user_prompt = f"""# Dev Agent - Iteration {iteration_num}

## Feature ID
{feature_id}

## Focus
{iteration['focus']}

## Specifications

### ADRs
{adrs}

### Technical Spec
{technical_spec}

### Design Spec
{design_spec}

---

## Task

Generate UP TO {iteration['max_files']} files for: **{iteration['focus']}**

Skip files already generated:
{generated_list}

## Output Format

```json
{{
  "implementation_summary": "What was generated in THIS iteration",
  "files_created": [
    {{"path": "path/to/file", "description": "Purpose", "content": "Escaped content"}}
  ],
  "tests_created": [],
  "documentation_updates": [],
  "quality_checklist": {{"style_guidelines": true, "tests_passing": true, "security_reviewed": true, "performance_validated": true}},
  "technical_debt": [],
  "next_steps": ""
}}
```

**CRITICAL**: 
- Escape newlines as \\n
- Escape quotes as \\"
- Escape backslashes as \\\\
- Maximum {iteration['max_files']} files
- Return empty arrays if no files match this iteration's focus
"""

    # Invoke AI API
    try:
        if AI_PROVIDER == "gemini":
            result = _invoke_gemini(system_prompt, user_prompt)
        else:
            result = _invoke_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        print(f"Error in iteration: {e}", file=sys.stderr)
        # Return empty result to continue
        return {
            "implementation_summary": f"Iteration failed: {e}",
            "files_created": [],
            "tests_created": [],
            "documentation_updates": [],
            "quality_checklist": {},
            "technical_debt": [],
            "next_steps": ""
        }


def _invoke_openai(system_prompt, user_prompt):
    """Invoke OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")
    
    import openai
    client = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        max_tokens=4000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


def _invoke_gemini(system_prompt, user_prompt):
    """Invoke Google Gemini API with retry logic."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    
    from google import genai
    client = genai.Client(api_key=api_key)
    
    combined_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
    
    # Retry logic for rate limits
    max_retries = 3
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=combined_prompt,
                config={
                    "temperature": float(os.getenv("TEMPERATURE", "0.7")),
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json"
                }
            )
            break
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"⏳ Rate limit. Waiting {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise
    
    # Parse response
    response_text = response.text.strip()
    
    if response_text.startswith("```"):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        # Save error
        error_file = f"dev_iteration_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"JSON parse error. Saved to {error_file}", file=sys.stderr)
        raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_dev_agent_iterative.py <feature_id>")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    
    print(f"💻 Dev Agent (Iterative) for: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    
    try:
        result = invoke_dev_agent_iterative(feature_id)
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)
    
    # Check for recovery note
    if "_recovery_note" in result:
        print(f"\n⚠️  Partial recovery: {result['_recovery_note']}")
    
    print(f"\n✅ Dev Agent complete!")
    print(f"\nImplementation Summary:")
    print(result.get('implementation_summary', 'No summary'))
    
    # Validate files
    files_created = result.get('files_created', [])
    tests_created = result.get('tests_created', [])
    
    if not files_created and not tests_created:
        print(f"\n⚠️  WARNING: No files generated!")
        sys.exit(1)
    
    # Create all files
    for file_info in files_created:
        filepath = REPO_ROOT / file_info['path']
        save_file(filepath, file_info['content'])
        print(f"  ✓ Created: {file_info['path']}")
    
    for test_info in tests_created:
        filepath = REPO_ROOT / test_info['path']
        save_file(filepath, test_info['content'])
        print(f"  ✓ Created test: {test_info['path']}")
    
    if files_created or tests_created:
        print(f"\n📦 Generated {len(files_created)} files and {len(tests_created)} tests")
    
    # Update documentation
    for doc_info in result.get('documentation_updates', []):
        filepath = REPO_ROOT / doc_info['path']
        save_file(filepath, doc_info['content'])
        print(f"  ✓ Updated docs: {doc_info['path']}")
    
    # Update pipeline state
    state_file = REPO_ROOT / ".ai/pipeline" / f"{feature_id}.state"
    if state_file.exists():
        state_content = load_file(state_file)
        state_content = state_content.replace('status: architect_approved', 'status: dev_awaiting_approval')
        state_content = state_content.replace('dev: pending', 'dev: in-progress')
        save_file(state_file, state_content)
        print(f"  ✓ Updated pipeline state")
    
    print(f"\n📋 Quality Checklist:")
    checklist = result.get('quality_checklist', {})
    for check, passed in checklist.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check.replace('_', ' ').title()}")
    
    if result.get('technical_debt'):
        print(f"\n⚠️  Technical Debt:")
        for debt in result['technical_debt']:
            print(f"  - [{debt['priority'].upper()}] {debt['description']}")
    
    print(f"\n🔜 Next Steps:")
    print(f"  {result.get('next_steps', 'Standard QA testing')}")


if __name__ == "__main__":
    main()
