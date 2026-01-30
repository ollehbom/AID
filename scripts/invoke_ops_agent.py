#!/usr/bin/env python3
"""
Ops Agent Executor
Invokes the Ops Agent for CI/CD, deployment, and GitOps configuration.
Based on SE GitOps/CI Specialist - makes deployments boring and reliable.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MODEL = os.getenv("MODEL", "gpt-4.1")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "openai" or "gemini"
REPO_ROOT = Path(__file__).parent.parent
AGENT_FILE = REPO_ROOT / ".ai/agents/ops.md"


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


def invoke_ops_agent(feature_id):
    """
    Invoke the Ops Agent to create deployment configurations and CI/CD updates.
    
    Args:
        feature_id: Identifier for this feature
        
    Returns:
        dict: Results including deployment configs and monitoring setup
    """
    print("Invoking Ops Agent...")
    
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    if agent_instructions.startswith("[File not found"):
        agent_instructions = """You are a GitOps & CI specialist. Make deployments boring and reliable.

## Mission: Prevent 3AM Deployment Disasters
Build reliable CI/CD pipelines, ensure safe deployments, focus on automation, monitoring, and rapid recovery.

## Core Principles
- RELIABILITY: Every deployment should be safe and predictable
- AUTOMATION: Manual steps are opportunities for errors
- MONITORING: You can't fix what you can't see
- RECOVERY: Plan for rollbacks before you need them

## Standards
- Security: Never commit secrets, use secret management
- Testing: All pipelines must include automated tests
- Monitoring: Health checks and alerting required
- Documentation: Runbooks for common issues
"""
    
    # Load implementation context
    technical_spec_file = REPO_ROOT / "design/technical-specs" / f"{feature_id}.md"
    technical_spec = load_file(technical_spec_file)
    
    # Check for existing workflow files to understand current CI/CD setup
    existing_workflows = list((REPO_ROOT / ".github/workflows").glob("*.yml"))
    existing_configs = "\n".join([f"- {wf.name}" for wf in existing_workflows])
    
    # Construct the prompt
    system_prompt = f"""{agent_instructions}

You are now executing as the Ops Agent in the AID pipeline.

Your task is to create deployment configurations, CI/CD updates, and monitoring setup.

## Your Responsibilities

### 1. CI/CD Pipeline Configuration
- Update or create GitHub Actions workflows
- Ensure proper testing gates
- Configure deployment strategies (rolling, blue-green, canary)
- Set up automated rollback mechanisms

### 2. Security & Secrets Management
- Document required secrets and environment variables
- Create .env.example templates
- Never commit actual secrets
- Use GitHub Secrets or secret management tools

### 3. Monitoring & Alerting
- Health check endpoints
- Performance thresholds
- Alert configurations
- Dashboard requirements

### 4. Deployment Documentation
- Deployment procedures
- Rollback procedures
- Troubleshooting guides
- Escalation criteria
"""

    user_prompt = f"""# Ops Agent Task

## Feature ID
{feature_id}

## Context Files

### Technical Specification
{technical_spec}

### Existing CI/CD Workflows
{existing_configs}

---

## Your Task

Create deployment and operations configurations for this feature. Provide:

1. **CI/CD Configuration**
   - GitHub Actions workflow updates (if needed)
   - Build and test automation
   - Deployment automation
   - Environment-specific configurations

2. **Deployment Strategy**
   - Choose appropriate strategy (rolling/blue-green/canary)
   - Define deployment steps
   - Configure health checks
   - Set up rollback procedures

3. **Security Configuration**
   - List required secrets/environment variables
   - Create .env.example template
   - Document secret rotation procedures
   - Security scanning configuration

4. **Monitoring Setup**
   - Health check endpoints specification
   - Performance metrics to track
   - Alert thresholds and channels
   - Dashboard configuration

5. **Operations Documentation**
   - Deployment runbook
   - Rollback procedures
   - Common issues and solutions
   - Escalation criteria

## Output Format

Provide your response in JSON format with these keys:

```json
{{
  "deployment_summary": "Overview of deployment approach and key decisions",
  "workflow_files": [
    {{"path": ".github/workflows/filename.yml", "description": "Purpose", "content": "Full YAML content"}}
  ],
  "config_files": [
    {{"path": "path/to/config", "description": "Purpose", "content": "Full content"}}
  ],
  "env_template": {{
    "path": ".env.example",
    "variables": [
      {{"name": "VAR_NAME", "description": "What this variable is for", "example": "example_value"}}
    ]
  }},
  "monitoring": {{
    "health_checks": [
      {{"endpoint": "/health", "expected_status": 200, "timeout_ms": 5000}}
    ],
    "metrics": [
      {{"name": "response_time_p95", "threshold": "500ms", "alert": "slack"}}
    ],
    "alerts": [
      {{"severity": "critical", "condition": "error_rate > 1%", "channel": "pagerduty"}}
    ]
  }},
  "documentation": [
    {{"path": "docs/deployment.md", "title": "Deployment Runbook", "content": "Full markdown content"}}
  ],
  "security_checklist": {{
    "secrets_managed": true,
    "env_vars_documented": true,
    "security_scanning": true,
    "branch_protection": true
  }},
  "rollback_procedure": "Step-by-step rollback instructions",
  "known_risks": [
    {{"risk": "Description", "mitigation": "How to handle it", "severity": "low|medium|high"}}
  ]
}}
```

Remember:
- Every deployment must be safe and reversible
- Automation over manual processes
- Monitor everything critical
- Document for 3AM debugging scenarios
- Security first, always
"""

    # Invoke AI API based on provider
    try:
        if AI_PROVIDER == "gemini":
            result = _invoke_gemini(system_prompt, user_prompt)
        else:
            result = _invoke_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        print(f"Error invoking Ops Agent: {e}", file=sys.stderr)
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
        max_tokens=8000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


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
    
    # Clean and parse response
    response_text = response.text.strip()
    
    # Try to extract JSON if wrapped in markdown code blocks
    if response_text.startswith("```"):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response. Error: {e}", file=sys.stderr)
        
        # Save full response for debugging
        error_file = f"ops_agent_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"Full response saved to {error_file}", file=sys.stderr)
        
        # Show context around the error
        if hasattr(e, 'pos') and e.pos:
            start = max(0, e.pos - 200)
            end = min(len(response_text), e.pos + 200)
            print(f"\nContext around error position:", file=sys.stderr)
            print(f"...{response_text[start:end]}...", file=sys.stderr)
        
        # Try to recover by truncating at the error position and closing the JSON
        print(f"\nAttempting JSON recovery...", file=sys.stderr)
        try:
            if hasattr(e, 'pos') and e.pos:
                # Find the last complete key-value pair before the error
                truncated = response_text[:e.pos]
                # Find last comma or opening brace
                last_comma = truncated.rfind(',')
                if last_comma > 0:
                    truncated = truncated[:last_comma]
                # Close the JSON object/arrays properly
                open_braces = truncated.count('{') - truncated.count('}')
                open_brackets = truncated.count('[') - truncated.count(']')
                truncated = truncated.rstrip()
                for _ in range(open_brackets):
                    truncated += "]"
                for _ in range(open_braces):
                    truncated += "}"
                
                recovered = json.loads(truncated)
                print(f"✓ Recovered partial JSON with {len(recovered)} top-level fields", file=sys.stderr)
                recovered["_recovery_note"] = f"JSON was truncated due to parsing error at position {e.pos}. Some content may be incomplete."
                return recovered
        except Exception as recovery_error:
            print(f"Recovery failed: {recovery_error}", file=sys.stderr)
        
        print(f"\nTip: Gemini generated invalid JSON. Check {error_file} for full output.", file=sys.stderr)
        print(f"Consider using OpenAI instead (better JSON handling).", file=sys.stderr)
        raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_ops_agent.py <feature_id>")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    
    print(f"🚀 Invoking Ops Agent for feature: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    print()
    
    # Invoke the agent
    try:
        result = invoke_ops_agent(feature_id)
    except Exception as e:
        print(f"❌ Failed to invoke Ops Agent: {e}")
        sys.exit(1)
    
    print(f"✅ Ops Agent execution complete!")
    print(f"\nDeployment Summary:")
    print(result.get('deployment_summary', 'No summary provided'))
    
    # Create workflow files
    for file_info in result.get('workflow_files', []):
        filepath = REPO_ROOT / file_info['path']
        save_file(filepath, file_info['content'])
        print(f"  ✓ Created workflow: {file_info['path']}")
    
    # Create config files
    for config_info in result.get('config_files', []):
        filepath = REPO_ROOT / config_info['path']
        save_file(filepath, config_info['content'])
        print(f"  ✓ Created config: {config_info['path']}")
    
    # Create .env.example
    if 'env_template' in result:
        env_content = "# Environment Variables\n\n"
        for var in result['env_template']['variables']:
            env_content += f"# {var['description']}\n"
            env_content += f"{var['name']}={var['example']}\n\n"
        filepath = REPO_ROOT / result['env_template']['path']
        save_file(filepath, env_content)
        print(f"  ✓ Created: {result['env_template']['path']}")
    
    # Create documentation
    for doc_info in result.get('documentation', []):
        filepath = REPO_ROOT / doc_info['path']
        save_file(filepath, doc_info['content'])
        print(f"  ✓ Created docs: {doc_info['path']}")
    
    # Update pipeline state
    state_file = REPO_ROOT / ".ai/pipeline" / f"{feature_id}.state"
    if state_file.exists():
        state_content = load_file(state_file)
        state_content = state_content.replace('status: dev_approved', 'status: ops_awaiting_approval')
        state_content = state_content.replace('ops: pending', 'ops: in-progress')
        save_file(state_file, state_content)
        print(f"  ✓ Updated pipeline state")
    
    print(f"\n📊 Monitoring Configuration:")
    monitoring = result.get('monitoring', {})
    if monitoring.get('health_checks'):
        print(f"  Health Checks: {len(monitoring['health_checks'])} configured")
    if monitoring.get('metrics'):
        print(f"  Metrics: {len(monitoring['metrics'])} tracked")
    if monitoring.get('alerts'):
        print(f"  Alerts: {len(monitoring['alerts'])} configured")
    
    print(f"\n🔒 Security Checklist:")
    checklist = result.get('security_checklist', {})
    for check, passed in checklist.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check.replace('_', ' ').title()}")
    
    if result.get('known_risks'):
        print(f"\n⚠️  Known Risks:")
        for risk in result['known_risks']:
            print(f"  - [{risk['severity'].upper()}] {risk['risk']}")
            print(f"    Mitigation: {risk['mitigation']}")
    
    print(f"\n🔄 Rollback Procedure:")
    print(f"  {result.get('rollback_procedure', 'Standard rollback via git revert')}")


if __name__ == "__main__":
    main()
