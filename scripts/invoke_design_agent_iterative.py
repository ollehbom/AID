#!/usr/bin/env python3
"""
Design Agent Executor - Iterative Approach
Invokes the Design Agent in multiple smaller iterations to avoid large JSON responses.
This prevents JSON parsing errors by requesting smaller, focused outputs.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from json_fixer import parse_json_with_recovery

# Load environment variables from .env file
load_dotenv()

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


def invoke_design_agent_iterative(feature_id, design_context=""):
    """
    Invoke the Design Agent iteratively with smaller requests.
    
    Args:
        feature_id: Identifier for this feature/experiment
        design_context: Optional additional context for design
    
    Returns:
        dict with design_intent, design_spec, wireframe_json, validation_notes
    """
    print("📋 Design Agent - Iterative Mode", file=sys.stderr)
    print("   Breaking down into smaller requests to avoid JSON errors...", file=sys.stderr)
    
    # Load agent instructions and context
    agent_instructions = load_file(AGENT_FILE)
    
    decision_file = None
    for decision_path in (REPO_ROOT / "product/decisions").glob(f"*{feature_id}*.md"):
        decision_file = load_file(decision_path)
        break
    
    if not decision_file:
        decision_file = "[Product decision not found]"
    
    experiments = load_file(EXPERIMENTS_FILE)
    beliefs = load_file(BELIEFS_FILE)
    
    # Base system prompt for all iterations
    base_system_prompt = f"""{agent_instructions}

You are the Design Agent in the AID pipeline. You translate product decisions into interaction designs.
Focus on clarity, simplicity, and reducing user friction."""
    
    # Context that's shared across all iterations
    shared_context = f"""## Context

### Product Decision
{decision_file}

### Active Experiments
{experiments[:500]}...

### Current Beliefs
{beliefs[:500]}...

{"### Additional Context" if design_context else ""}
{design_context if design_context else ""}
"""
    
    # Iteration 1: Design Intent
    print("\n📝 Step 1/4: Creating design intent...", file=sys.stderr)
    intent_prompt = f"""{shared_context}

## Task: Create Design Intent

Write the design intent for feature: {feature_id}

Answer these questions:
- Why does this feature exist?
- How should it feel to users?
- What principles guide the interaction?
- What user needs does it address?

Provide response as JSON:
{{
  "design_intent": "Complete markdown content for the design intent document"
}}

Keep it concise but comprehensive (300-500 words).
"""
    
    intent_result = _invoke_ai(base_system_prompt, intent_prompt)
    design_intent = intent_result.get("design_intent", "")
    print(f"   ✓ Intent created ({len(design_intent)} chars)", file=sys.stderr)
    
    # Iteration 2: Design Specification
    print("\n📋 Step 2/4: Creating design specification...", file=sys.stderr)
    spec_prompt = f"""{shared_context}

## Previously Created
Design Intent: {design_intent[:200]}...

## Task: Create Design Specification

Create a detailed design specification for feature: {feature_id}

Include:
1. Complete user flow (step by step)
2. All possible states (loading, error, success, empty)
3. Exact copy/microcopy for each state
4. Error handling and edge cases
5. Transitions and animations (if relevant)

Provide response as JSON:
{{
  "design_spec": "Complete markdown content for the design specification"
}}

Be thorough but focused (500-800 words).
"""
    
    spec_result = _invoke_ai(base_system_prompt, spec_prompt)
    design_spec = spec_result.get("design_spec", "")
    print(f"   ✓ Spec created ({len(design_spec)} chars)", file=sys.stderr)
    
    # Iteration 3: Wireframe (Simple Structure)
    print("\n🎨 Step 3/4: Creating wireframe...", file=sys.stderr)
    wireframe_prompt = f"""{shared_context}

## Previously Created
Design Intent: {design_intent[:200]}...
Design Spec: {design_spec[:300]}...

## Task: Create Wireframe JSON

Create a simple, structured wireframe for feature: {feature_id}

Use this format (keep it SIMPLE):
{{
  "wireframe": {{
    "name": "ScreenName",
    "type": "FRAME",
    "width": 375,
    "height": 812,
    "children": [
      {{"type": "TEXT", "content": "Header", "fontSize": 24}},
      {{"type": "BUTTON", "label": "Action", "variant": "primary"}}
    ]
  }}
}}

Guidelines:
- Use flat structure when possible
- Limit nesting depth
- Include only essential UI elements
- Use semantic names
- Keep JSON simple and clean

Provide response as JSON with the wireframe object directly (not as a string).
"""
    
    wireframe_result = _invoke_ai(base_system_prompt, wireframe_prompt)
    wireframe_json = wireframe_result.get("wireframe", {})
    print(f"   ✓ Wireframe created ({len(json.dumps(wireframe_json))} chars)", file=sys.stderr)
    
    # Iteration 4: Validation
    print("\n✓ Step 4/4: Creating validation notes...", file=sys.stderr)
    validation_prompt = f"""{shared_context}

## Previously Created
Design Intent: {design_intent[:200]}...
Design Spec: {design_spec[:200]}...
Wireframe: Created with {len(wireframe_json.get('children', []))} elements

## Task: Validation Check

Review the design against these validation rules:
- Can a new user predict what happens next?
- Is anything explained too late?
- Does the UI match the intent?

Identify:
- Any concerns or friction points
- Areas needing clarification
- Potential usability issues

Provide response as JSON:
{{
  "validation_notes": "Your validation findings (200-400 words)",
  "summary": "Brief 2-3 sentence summary of the overall design approach"
}}
"""
    
    validation_result = _invoke_ai(base_system_prompt, validation_prompt)
    validation_notes = validation_result.get("validation_notes", "")
    summary = validation_result.get("summary", "")
    print(f"   ✓ Validation complete ({len(validation_notes)} chars)", file=sys.stderr)
    
    # Combine all results
    combined_result = {
        "design_intent": design_intent,
        "design_spec": design_spec,
        "wireframe_json": wireframe_json,
        "validation_notes": validation_notes,
        "summary": summary
    }
    
    print("\n✅ All design components created successfully!", file=sys.stderr)
    
    return combined_result


def _invoke_ai(system_prompt, user_prompt):
    """Invoke AI based on configured provider."""
    if AI_PROVIDER == "gemini":
        return _invoke_gemini(system_prompt, user_prompt)
    else:
        return _invoke_openai(system_prompt, user_prompt)


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
        max_tokens=8192,  # Increased to accommodate full design specifications
        response_format={"type": "json_object"}
    )
    
    return parse_json_with_recovery(
        response.choices[0].message.content,
        error_prefix="design_iteration_error"
    )


def _invoke_gemini(system_prompt, user_prompt):
    """Invoke Google Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    
    from google import genai
    client = genai.Client(api_key=api_key)
    
    combined_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
    
    response = client.models.generate_content(
        model=MODEL,
        contents=combined_prompt,
        config={
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_output_tokens": 8192,  # Increased to accommodate full design specifications
            "response_mime_type": "application/json"
        }
    )
    
    return parse_json_with_recovery(
        response.text,
        error_prefix="design_iteration_error"
    )


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_design_agent_iterative.py <feature_id> [design_context]")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    design_context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🎨 Design Agent (Iterative) for: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    
    try:
        result = invoke_design_agent_iterative(feature_id, design_context)
    except Exception as e:
        print(f"\n❌ Design Agent failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n📊 Results Summary:")
    print(f"  Intent: {len(result.get('design_intent', ''))} chars")
    print(f"  Spec: {len(result.get('design_spec', ''))} chars")
    print(f"  Wireframe: {len(json.dumps(result.get('wireframe_json', {})))} chars")
    print(f"  Validation: {len(result.get('validation_notes', ''))} chars")
    
    # Save outputs
    output_dir = REPO_ROOT / "design"
    
    # Save design intent
    intent_file = output_dir / "intents" / f"{feature_id}.md"
    save_file(intent_file, result["design_intent"])
    print(f"\n✓ Saved: {intent_file}")
    
    # Save design spec
    spec_file = output_dir / "specs" / f"{feature_id}.md"
    save_file(spec_file, result["design_spec"])
    print(f"✓ Saved: {spec_file}")
    
    # Save wireframe
    wireframe_file = output_dir / "wireframes" / f"{feature_id}.json"
    save_file(wireframe_file, json.dumps(result["wireframe_json"], indent=2))
    print(f"✓ Saved: {wireframe_file}")
    
    # Save validation
    validation_file = output_dir / "validations" / f"{feature_id}.md"
    save_file(validation_file, result["validation_notes"])
    print(f"✓ Saved: {validation_file}")
    
    print(f"\n✅ Design Agent complete!")
    print(f"\nSummary: {result.get('summary', 'N/A')}")


if __name__ == "__main__":
    main()
