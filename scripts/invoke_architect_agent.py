#!/usr/bin/env python3
"""
Architect Agent Executor
Invokes the Architect Agent using AI models to review and validate system architecture.
"""

import os
import sys
import json
import re
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
AGENT_FILE = REPO_ROOT / ".ai/agents/architect.md"
PRODUCT_DECISIONS = REPO_ROOT / "product/decisions"
DESIGN_SPECS = REPO_ROOT / "design/specs"
DESIGN_INTENTS = REPO_ROOT / "design/intents"
EXPERIMENTS = REPO_ROOT / "experiments/active.md"
ARCHITECTURE_DIR = REPO_ROOT / "design/architecture"
TECHNICAL_SPECS_DIR = REPO_ROOT / "design/technical-specs"


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


def get_next_adr_number():
    """Get the next ADR number by scanning existing ADRs."""
    if not ARCHITECTURE_DIR.exists():
        return 1
    
    adr_files = list(ARCHITECTURE_DIR.glob("ADR-*.md"))
    if not adr_files:
        return 1
    
    numbers = []
    for f in adr_files:
        match = re.match(r"ADR-(\d+)", f.name)
        if match:
            numbers.append(int(match.group(1)))
    
    return max(numbers) + 1 if numbers else 1


def invoke_architect_agent(feature_id):
    """
    Invoke the Architect Agent to review architecture and create technical specs.
    
    Args:
        feature_id: Identifier for this feature/experiment
    
    Returns:
        dict with adr_content, technical_spec, adr_number, complexity
    """
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    
    # Load context files
    product_decision = load_file(PRODUCT_DECISIONS / f"{datetime.now().strftime('%Y-%m-%d')}-{feature_id}.md")
    design_spec = load_file(DESIGN_SPECS / f"{feature_id}.md")
    design_intent = load_file(DESIGN_INTENTS / f"{feature_id}.md")
    experiments = load_file(EXPERIMENTS)
    
    # Get next ADR number
    adr_number = get_next_adr_number()
    
    # Construct the prompt
    system_prompt = f"""{agent_instructions}

You are now executing as the Architect Agent in the AID pipeline.

Your task is to review the architectural implications of this change and produce structured outputs according to your role.
"""

    user_prompt = f"""# Architect Agent Task

## Feature ID
{feature_id}

## Context Files

### Product Decision Record
{product_decision}

### Design Intent (if applicable)
{design_intent}

### Design Spec (if applicable)
{design_spec}

### Active Experiments
{experiments}

---

## Your Task

Review this change from an architectural perspective and create:

1. **Architecture Decision Record (ADR-{adr_number:03d})**
   - Follow the ADR template from your instructions
   - Include context, decision drivers, options considered
   - Document the chosen approach with rationale
   - Note consequences (positive, negative, risks)
   - Provide implementation guidance

2. **Technical Specification**
   - Architecture overview
   - Component breakdown
   - Data models and APIs
   - Infrastructure requirements
   - Testing strategy
   - Deployment approach

3. **Architecture Assessment**
   - Complexity level (simple, moderate, complex)
   - Primary concerns (security, performance, cost, reliability)
   - Scale considerations
   - Risk assessment

Apply the Well-Architected Framework focusing on:
- Security (Zero Trust, least privilege)
- Reliability (fallbacks, error handling)
- Performance (scaling, optimization)
- Cost (right-sizing, efficiency)
- Operational Excellence (monitoring, testing)

## Output Format

Provide your response in JSON format with these keys:

```json
{{
  "adr_content": "Full markdown content for ADR-{adr_number:03d}-{feature_id}.md",
  "technical_spec": "Full markdown content for technical-specs/{feature_id}.md",
  "complexity": "simple|moderate|complex",
  "primary_concerns": ["security", "performance", "cost", "reliability"],
  "summary": "Brief 2-3 sentence summary of architectural approach"
}}
```
"""

    # Invoke AI API based on provider
    try:
        if AI_PROVIDER == "gemini":
            result = _invoke_gemini(system_prompt, user_prompt)
        else:
            result = _invoke_openai(system_prompt, user_prompt)
        
        # Add ADR number to result
        result["adr_number"] = adr_number
        
        return result
        
    except Exception as e:
        print(f"Error invoking Architect Agent: {e}", file=sys.stderr)
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
        error_prefix="architect_agent_error"
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
        error_prefix="architect_agent_error"
    )


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_architect_agent.py <feature_id>")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    
    print(f"🏗️ Invoking Architect Agent for feature: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    print()
    
    # Invoke the agent
    try:
        result = invoke_architect_agent(feature_id)
    except Exception as e:
        print(f"❌ Failed to invoke Architect Agent: {e}")
        sys.exit(1)
    
    # Save ADR
    adr_number = result["adr_number"]
    adr_path = ARCHITECTURE_DIR / f"ADR-{adr_number:03d}-{feature_id}.md"
    save_file(adr_path, result["adr_content"])
    print(f"✅ Created ADR: {adr_path.relative_to(REPO_ROOT)}")
    
    # Save technical spec
    tech_spec_path = TECHNICAL_SPECS_DIR / f"{feature_id}.md"
    save_file(tech_spec_path, result["technical_spec"])
    print(f"✅ Created technical spec: {tech_spec_path.relative_to(REPO_ROOT)}")
    
    # Update pipeline state
    state_path = REPO_ROOT / f".ai/pipeline/{feature_id}.state"
    if state_path.exists():
        state_content = load_file(state_path)
        
        # Update status
        state_content = re.sub(r'status:.*', 'status: architect_complete', state_content)
        state_content = re.sub(r'architect: pending', f'architect: ✓ {datetime.now().strftime("%Y-%m-%d")}', state_content)
        
        # Add architecture section if not exists
        if 'architecture:' not in state_content:
            arch_section = f"""architecture:
  adr_number: ADR-{adr_number:03d}
  complexity: {result['complexity']}
  primary_concerns: {result.get('primary_concerns', [])}
  review_date: {datetime.now().strftime('%Y-%m-%d')}
"""
            state_content = state_content.rstrip() + "\n" + arch_section
        
        save_file(state_path, state_content)
        print(f"✅ Updated pipeline state: {state_path.relative_to(REPO_ROOT)}")
    
    # Print summary
    print()
    print("📋 Summary:")
    print(result["summary"])
    print()
    print(f"🏗️ Complexity: {result['complexity']}")
    print(f"🎯 Primary Concerns: {', '.join(result.get('primary_concerns', []))}")
    print(f"📝 ADR Number: ADR-{adr_number:03d}")
    print()
    print("✅ Architect Agent execution complete!")
    print("👉 Next: Dev Agent will implement according to architectural guidelines")


if __name__ == "__main__":
    main()
