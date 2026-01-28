#!/usr/bin/env python3
"""
Product Agent Executor
Invokes the Product Agent using OpenAI GPT-4.1 to analyze feedback and create experiments.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MODEL = os.getenv("MODEL", "gpt-4.1")
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

{f"### Additional Context\n{feedback_context}\n" if feedback_context else ""}

---

## Your Task

Analyze the feedback in the inbox and create the following outputs:

1. **Product Decision Record** (product/decisions/{feature_id}.md)
   - Follow the template from your GitHub Issue Creation section
   - Include hypothesis, context, experiment scope, success evaluation
   - Reference affected beliefs explicitly

2. **Experiment Update** (experiments/active.md - append/update)
   - Add the new experiment with ID EXP-{datetime.now().strftime('%Y-%m-%d')}-{feature_id.upper()}
   - Include belief, change, owner, status, success signal

3. **GitHub Issue Content**
   - Complete issue following your template
   - Include all required labels
   - Ensure measurable success criteria

4. **Belief Update** (if needed)
   - Note if any belief should be updated in product/beliefs/current.md
   - Specify what changed and why

## Output Format

Provide your response in JSON format with these keys:

```json
{{
  "decision_record": "Full markdown content for product/decisions/{feature_id}.md",
  "experiment_update": "Content to append to experiments/active.md",
  "github_issue": "Full GitHub issue markdown content",
  "belief_update": "Updated beliefs section or 'NO_CHANGE' if no update needed",
  "summary": "Brief 2-3 sentence summary of the decision"
}}
```

Begin your analysis and generate the outputs now.
"""

    # Call OpenAI API
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment. Create a .env file with your API key.")
        
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
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error invoking Product Agent: {e}", file=sys.stderr)
        raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_product_agent.py <feature_id> [feedback_context]")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    feedback_context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🤖 Invoking Product Agent for feature: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
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
    
    # Print summary
    print()
    print("📋 Summary:")
    print(result["summary"])
    print()
    print("✅ Product Agent execution complete!")
    print("👉 Next: Design Agent will process this in the next pipeline stage")


if __name__ == "__main__":
    main()
