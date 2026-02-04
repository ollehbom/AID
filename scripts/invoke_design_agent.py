#!/usr/bin/env python3
"""
Design Agent Executor
Invokes the Design Agent using AI models (OpenAI GPT-4.1 or Google Gemini 2.5 Pro).
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from json_fixer import parse_json_with_recovery
from pydantic import BaseModel
from typing import Any, Dict

# Load environment variables from .env file
load_dotenv()

# Pydantic Model for Schema Validation
class DesignAgentResponse(BaseModel):
    """Type-safe response structure for Design Agent."""
    design_intent: str
    design_spec: str
    wireframe_json: str  # JSON as string to avoid additionalProperties
    validation_checklist: str
    summary: str

# Configuration
MODEL = os.getenv("MODEL", "gpt-4.1")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "openai" or "gemini"
REPO_ROOT = Path(__file__).parent.parent
AGENT_FILE = REPO_ROOT / ".ai/agents/design.md"
BELIEFS_FILE = REPO_ROOT / "product/beliefs/current.md"
EXPERIMENTS_FILE = REPO_ROOT / "experiments/active.md"


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


def invoke_design_agent(feature_id, design_context=""):
    """
    Invoke the Design Agent to create design intent, specs, and wireframes.
    
    Args:
        feature_id: Identifier for this feature/experiment
        design_context: Optional additional context for design
    
    Returns:
        dict with design_intent, design_spec, wireframe_json, validation_notes
    """
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    
    # Load context files
    decision_file = None
    for decision_path in (REPO_ROOT / "product/decisions").glob(f"*{feature_id}*.md"):
        decision_file = load_file(decision_path)
        break
    
    if not decision_file:
        decision_file = "[Product decision not found - this should not happen in normal pipeline flow]"
    
    experiments = load_file(EXPERIMENTS_FILE)
    beliefs = load_file(BELIEFS_FILE)
    
    # Construct the prompt
    system_prompt = f"""{agent_instructions}

You are now executing as the Design Agent in the AID pipeline.

Your task is to translate product decisions into interaction designs with clear intent and validation.
"""

    user_prompt = f"""# Design Agent Task

## Feature ID
{feature_id}

## Context Files

### Product Decision
{decision_file}

### Active Experiments
{experiments}

### Current Beliefs
{beliefs}

{"### Additional Context" if design_context else ""}
{design_context if design_context else ""}

---

## Your Task

Based on the product decision, create the following design outputs:

1. **Design Intent** (design/intents/{feature_id}.md)
   - Why this feature exists
   - How it should feel to users
   - What principles guide the interaction
   - What user needs it addresses

2. **Design Specification** (design/specs/{feature_id}.md)
   - Complete user flow (step by step)
   - All possible states (loading, error, success, empty)
   - Exact copy/microcopy for each state
   - Error handling and edge cases
   - Transitions and animations (if relevant)

3. **Wireframe JSON** (design/wireframes/{feature_id}.json)
   - Follow the Wireframe JSON Format from your instructions
   - Create a structured, implementable layout
   - Include all key UI elements
   - Use semantic naming
   - Specify sizing, spacing, and hierarchy
   - KEEP IT SIMPLE: Use minimal nesting and straightforward structure

4. **Validation Notes**
   - Check against validation rules:
     * Can a new user predict what happens next?
     * Is anything explained too late?
     * Does the UI match the intent?
   - Note any concerns or friction points
   - Identify areas needing clarification

## Output Format

Provide your response as valid JSON. To avoid JSON escaping issues, provide wireframe as a JSON-formatted STRING (not an object).

```json
{{
  "design_intent": "Full markdown content for design/intents/{feature_id}.md",
  "design_spec": "Full markdown content for design/specs/{feature_id}.md",
  "wireframe_json_string": "Entire wireframe JSON as an escaped string - this makes it easier to handle",
  "validation_notes": "Validation findings and concerns",
  "summary": "Brief 2-3 sentence summary of the design approach"
}}
```

Example of wireframe_json_string (note it's a STRING containing JSON, properly escaped):
```json
{{
  "wireframe_json_string": "{{\\"name\\": \\"LoginScreen\\", \\"type\\": \\"FRAME\\", \\"children\\": []}}"
}}
```

Remember: 
- Your designs should reduce friction, match stated intent, and be immediately understandable to new users
- The wireframe_json_string should contain valid JSON, but AS A STRING VALUE
- Use simple structures to avoid nested escaping complexity
"""

    # Invoke AI API based on provider
    try:
        if AI_PROVIDER == "gemini":
            result = _invoke_gemini(system_prompt, user_prompt)
        else:
            result = _invoke_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        print(f"Error invoking Design Agent: {e}", file=sys.stderr)
        raise


def _invoke_openai(system_prompt, user_prompt):
    """Invoke OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment. Create a .env file with your API key.")
    
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
    
    return parse_json_with_recovery(
        response.choices[0].message.content,
        error_prefix="design_agent_error"
    )


def _invoke_gemini(system_prompt, user_prompt):
    """Invoke Google Gemini API with schema validation."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Create a .env file with your API key.")
    
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    
    # Combine system and user prompts for Gemini
    combined_prompt = f"""{system_prompt}

---

{user_prompt}"""
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=combined_prompt,
            config=types.GenerateContentConfig(
                temperature=float(os.getenv("TEMPERATURE", "0.7")),
                max_output_tokens=8192,
                response_mime_type='application/json',
                response_schema=DesignAgentResponse  # ✨ Schema validation!
            )
        )
        
        # Use validated, parsed response
        parsed = response.parsed
        # Parse wireframe JSON string into object
        try:
            wireframe_obj = json.loads(parsed.wireframe_json)
        except json.JSONDecodeError:
            wireframe_obj = {}  # Fallback to empty object
        
        return {
            "design_intent": parsed.design_intent,
            "design_spec": parsed.design_spec,
            "wireframe_json": wireframe_obj,
            "validation_checklist": parsed.validation_checklist,
            "summary": parsed.summary
        }
    
    except Exception as e:
        print(f"⚠️  Schema validation failed: {e}")
        # Try without schema validation as fallback
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=combined_prompt,
                config=types.GenerateContentConfig(
                    temperature=float(os.getenv("TEMPERATURE", "0.7")),
                    max_output_tokens=8192,
                    response_mime_type='application/json'
                    # No schema validation
                )
            )
            return parse_json_with_recovery(
                response.text,
                error_prefix="design_agent_error"
            )
        except Exception as fallback_error:
            raise Exception(f"Both schema validation and fallback failed: {e}, {fallback_error}")


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_design_agent.py <feature_id> [design_context]")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    design_context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🎨 Invoking Design Agent for feature: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    print()
    
    # Check pipeline state
    state_path = REPO_ROOT / f".ai/pipeline/{feature_id}.state"
    if not state_path.exists():
        print(f"❌ Pipeline state not found: {state_path.relative_to(REPO_ROOT)}")
        print("   Run the Product Agent first to create the pipeline state.")
        sys.exit(1)
    
    # Invoke the agent
    try:
        result = invoke_design_agent(feature_id, design_context)
    except Exception as e:
        print(f"❌ Failed to invoke Design Agent: {e}")
        sys.exit(1)
    
    # Save design intent
    intent_path = REPO_ROOT / f"design/intents/{feature_id}.md"
    save_file(intent_path, result["design_intent"])
    print(f"✅ Created design intent: {intent_path.relative_to(REPO_ROOT)}")
    
    # Save design spec
    spec_path = REPO_ROOT / f"design/specs/{feature_id}.md"
    save_file(spec_path, result["design_spec"])
    print(f"✅ Created design spec: {spec_path.relative_to(REPO_ROOT)}")
    
    # Save wireframe JSON
    wireframe_path = REPO_ROOT / f"design/wireframes/{feature_id}.json"
    # Handle wireframe as either string or object (for backward compatibility)
    if "wireframe_json_string" in result:
        # It's provided as a JSON string, parse it to validate and then save pretty-printed
        try:
            wireframe_obj = json.loads(result["wireframe_json_string"])
            save_file(wireframe_path, json.dumps(wireframe_obj, indent=2))
        except json.JSONDecodeError:
            # If it's not valid JSON, save as-is
            save_file(wireframe_path, result["wireframe_json_string"])
    else:
        # Legacy format: object directly
        save_file(wireframe_path, json.dumps(result.get("wireframe_json", {}), indent=2))
    print(f"✅ Created wireframe: {wireframe_path.relative_to(REPO_ROOT)}")
    
    # Save validation notes
    validation_path = REPO_ROOT / f"design/validations/{feature_id}.md"
    save_file(validation_path, result["validation_notes"])
    print(f"✅ Created validation notes: {validation_path.relative_to(REPO_ROOT)}")
    
    # Update pipeline state
    state_content = load_file(state_path)
    updated_state = state_content.replace(
        "design: pending",
        f"design: ✓ {datetime.now().strftime('%Y-%m-%d')}"
    ).replace(
        "status: product_complete",
        "status: design_complete"
    )
    save_file(state_path, updated_state)
    print(f"✅ Updated pipeline state: {state_path.relative_to(REPO_ROOT)}")
    
    # Print summary
    print()
    print("📋 Summary:")
    print(result["summary"])
    print()
    print("✅ Design Agent execution complete!")
    print("👉 Next: Architect Agent will process this in the next pipeline stage")


if __name__ == "__main__":
    main()
