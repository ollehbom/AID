#!/usr/bin/env python3
"""
Product Agent Executor
Invokes the Product Agent using AI models (OpenAI GPT-4.1 or Google Gemini 2.5 Pro).
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
AGENT_FILE = REPO_ROOT / ".ai/agents/product.md"
FEEDBACK_INBOX = REPO_ROOT / "product/feedback/inbox.md"
BELIEFS_FILE = REPO_ROOT / "product/beliefs/current.md"
DECISION_RULES = REPO_ROOT / ".ai/workflows/decision-rules.md"
CHANGE_INTAKE = REPO_ROOT / ".ai/workflows/change-intake.md"


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


def invoke_product_agent(feature_id, feedback_context=""):
    """
    Invoke the Product Agent to analyze feedback and create an experiment.
    
    Args:
        feature_id: Identifier for this feature/experiment
        feedback_context: Optional additional context about the feedback
    
    Returns:
        dict with decision_record, experiment_update, github_issue, belief_update
    """
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    
    # Load context files
    feedback = load_file(FEEDBACK_INBOX)
    beliefs = load_file(BELIEFS_FILE)
    decision_rules = load_file(DECISION_RULES)
    change_intake = load_file(CHANGE_INTAKE)
    
    # Construct the prompt
    system_prompt = f"""{agent_instructions}

You are now executing as the Product Agent in the AID pipeline.

Your task is to analyze the feedback and produce structured outputs according to your role.
"""

    user_prompt = f"""# Product Agent Task

## Feature ID
{feature_id}

## Context Files

### Current Feedback Inbox
{feedback}

### Current Beliefs
{beliefs}

### Decision Rules
{decision_rules}

### Change Intake Workflow
{change_intake}

{"### Additional Context" if feedback_context else ""}{feedback_context if feedback_context else ""}

---

## Your Task

Analyze the feedback in the inbox and create the following outputs:

1. **Product Decision Record** (product/decisions/{feature_id}.md)
   - Follow the template from your GitHub Issue Creation section
   - Include hypothesis, context, experiment scope, success evaluation
   - Reference affected beliefs explicitly

2. **Experiment Update** (experiments/active.md - append/update)
   - Add the new experiment with ID EXP-YYYY-MM-DD-FEATURE_ID
   - Include belief, change, owner, status, success signal

3. **GitHub Issue Content**
   - Complete issue following your template
   - Include all required labels
   - Ensure measurable success criteria

4. **Belief Update** (if needed)
   - Note if any belief should be updated in product/beliefs/current.md
   - Specify what changed and why

5. **Design Requirement Flag**
   - Set `needs_design: true` if this change requires UI/UX work (user-facing changes, flows, visual design)
   - Set `needs_design: false` if this is purely technical (backend, infrastructure, API changes with no UI impact)

## Output Format

Provide your response in JSON format with these keys:

```json
{{
  "decision_record": "Full markdown content for product/decisions/{feature_id}.md",
  "experiment_update": "Content to append to experiments/active.md",
  "github_issue": "Full GitHub issue markdown content",
  "belief_update": "Updated beliefs section or 'NO_CHANGE' if no update needed",
  "needs_design": true or false,
  "summary": "Brief 2-3 sentence summary of the decision"
}}
```
"""

    # Invoke AI API based on provider
    try:
        if AI_PROVIDER == "gemini":
            result = _invoke_gemini(system_prompt, user_prompt)
        else:
            result = _invoke_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        print(f"Error invoking Product Agent: {e}", file=sys.stderr)
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
        error_prefix="product_agent_error"
    )


def _invoke_gemini(system_prompt, user_prompt):
    """Invoke Google Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Create a .env file with your API key.")
    
    from google import genai
    client = genai.Client(api_key=api_key)
    
    # Combine system and user prompts for Gemini
    combined_prompt = f"""{system_prompt}

---

{user_prompt}"""
    
    response = client.models.generate_content(
        model=MODEL,
        contents=combined_prompt,
        config={
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
    )
    
    # Parse response with automatic error recovery
    return parse_json_with_recovery(
        response.text,
        error_prefix="product_agent_error"
    )


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_product_agent.py <feature_id> [feedback_context]")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    feedback_context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🤖 Invoking Product Agent for feature: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    print()
    
    # Invoke the agent
    try:
        result = invoke_product_agent(feature_id, feedback_context)
    except Exception as e:
        print(f"❌ Failed to invoke Product Agent: {e}")
        sys.exit(1)
    
    # Save decision record
    decision_path = REPO_ROOT / f"product/decisions/{datetime.now().strftime('%Y-%m-%d')}-{feature_id}.md"
    save_file(decision_path, result["decision_record"])
    print(f"✅ Created decision record: {decision_path.relative_to(REPO_ROOT)}")
    
    # Update experiments/active.md
    experiments_path = REPO_ROOT / "experiments/active.md"
    current_experiments = load_file(experiments_path)
    updated_experiments = current_experiments.rstrip() + "\n\n" + result["experiment_update"]
    save_file(experiments_path, updated_experiments)
    print(f"✅ Updated experiments: {experiments_path.relative_to(REPO_ROOT)}")
    
    # Save GitHub issue content
    issue_path = REPO_ROOT / f".ai/pipeline/{feature_id}-issue.md"
    save_file(issue_path, result["github_issue"])
    print(f"✅ Created GitHub issue content: {issue_path.relative_to(REPO_ROOT)}")
    
    # Update beliefs if needed
    if result["belief_update"] != "NO_CHANGE":
        beliefs_path = REPO_ROOT / "product/beliefs/current.md"
        save_file(beliefs_path, result["belief_update"])
        print(f"✅ Updated beliefs: {beliefs_path.relative_to(REPO_ROOT)}")
    
    # Create pipeline state file
    needs_design = result.get("needs_design", True)
    state_content = f"""feature: {feature_id}
status: product_complete
needs_design: {str(needs_design).lower()}
stages:
  product: ✓ {datetime.now().strftime('%Y-%m-%d')}
  design: {'pending' if needs_design else 'skipped'}
  architect: pending
  dev: pending
  qa: pending
  ops: pending
"""
    state_path = REPO_ROOT / f".ai/pipeline/{feature_id}.state"
    save_file(state_path, state_content)
    print(f"✅ Created pipeline state: {state_path.relative_to(REPO_ROOT)}")
    
    # Print summary
    print()
    print("📋 Summary:")
    print(result["summary"])
    print()
    print(f"🎯 Needs Design: {'Yes' if needs_design else 'No (purely technical)'}")
    print()
    print("✅ Product Agent execution complete!")
    next_stage = "Design Agent" if needs_design else "Architect Agent"
    print(f"👉 Next: {next_stage} will process this in the next pipeline stage")


if __name__ == "__main__":
    main()
