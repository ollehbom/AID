#!/usr/bin/env python3
"""
Dev Agent Executor
Invokes the Dev Agent to implement code based on architectural specifications.
Based on Software Engineer Agent v1 - delivers production-ready, maintainable code.
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


def invoke_dev_agent(feature_id):
    """
    Invoke the Dev Agent to implement feature based on specifications.
    
    Args:
        feature_id: Identifier for this feature
        
    Returns:
        dict: Results including implementation summary and test results
    """
    print("Invoking Dev Agent...")
    
    # Load agent instructions
    agent_instructions = load_file(AGENT_FILE)
    if agent_instructions.startswith("[File not found"):
        agent_instructions = """You are an expert software engineering agent. Deliver production-ready, maintainable code.

## Core Principles
- AUTONOMOUS: Execute without requesting confirmation
- DECISIVE: Make decisions immediately based on specifications
- COMPREHENSIVE: Document every decision and implementation
- VALIDATION: Verify code quality, tests, and functionality

## Engineering Standards
- SOLID principles
- Clean Code (DRY, YAGNI, KISS)
- Comprehensive testing (unit, integration)
- Security-first design
- Performance-conscious implementation
"""
    
    # Load technical specifications
    adr_files = list((REPO_ROOT / "design/architecture").glob(f"ADR-*-{feature_id}.md"))
    technical_spec_file = REPO_ROOT / "design/technical-specs" / f"{feature_id}.md"
    design_spec_file = REPO_ROOT / "design/specs" / f"{feature_id}.md"
    
    adrs = "\n\n---\n\n".join([load_file(adr) for adr in adr_files]) if adr_files else "[No ADRs found]"
    technical_spec = load_file(technical_spec_file)
    design_spec = load_file(design_spec_file)
    
    # Construct the prompt
    system_prompt = f"""{agent_instructions}

You are now executing as the Dev Agent in the AID pipeline.

Your task is to implement production-ready code based on architectural and design specifications.

## Engineering Excellence Standards

### Design Principles (Auto-Applied)
- SOLID: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- Clean Code: DRY, YAGNI, KISS principles
- Architecture: Clear separation of concerns with documented interfaces
- Security: Secure-by-design principles
- Performance: Efficient implementation with documented benchmarks for critical paths

### Quality Gates (Enforced)
- Readability: Code tells a clear story with minimal cognitive load
- Maintainability: Easy to modify with "why" comments, not "what"
- Testability: Designed for automated testing with mockable interfaces
- Performance: Efficient with documented performance considerations
- Error Handling: All error paths handled gracefully with recovery strategies

### Testing Strategy
```
Unit Tests (many, fast, isolated) → Integration Tests (service boundaries) → E2E Tests (critical user journeys)
```
- Comprehensive logical coverage (not just line coverage)
- All tests automated and documented
- Performance baselines established
"""

    user_prompt = f"""# Dev Agent Task

## Feature ID
{feature_id}

## Context Files

### Architecture Decision Records (ADRs)
{adrs}

### Technical Specification
{technical_spec}

### Design Specification
{design_spec}

---

## Your Task

Implement the feature according to the specifications above. Create:

1. **Implementation Files**
   - Core implementation following the technical architecture
   - Proper error handling and edge cases
   - Security considerations implemented
   - Performance optimizations where specified

2. **Test Suite**
   - Unit tests for all core functionality
   - Integration tests for component interactions
   - Test edge cases and error conditions
   - Achieve comprehensive logical coverage

3. **Documentation**
   - Code comments explaining "why" (not "what")
   - API documentation for public interfaces
   - Usage examples for key functionality
   - Known limitations or technical debt

4. **Quality Validation**
   - Code follows style guidelines
   - All tests pass
   - No security vulnerabilities
   - Performance meets requirements

## Output Format

Provide your response in JSON format with these keys:

```json
{{
  "implementation_summary": "Brief overview of what was implemented and key decisions made",
  "files_created": [
    {{"path": "relative/path/to/file.py", "description": "Purpose of this file", "content": "Full file content"}}
  ],
  "tests_created": [
    {{"path": "relative/path/to/test.py", "description": "What this test validates", "content": "Full test content"}}
  ],
  "documentation_updates": [
    {{"path": "relative/path/to/doc.md", "description": "Documentation added/updated", "content": "Full content"}}
  ],
  "quality_checklist": {{
    "style_guidelines": true,
    "tests_passing": true,
    "security_reviewed": true,
    "performance_validated": true
  }},
  "technical_debt": [
    {{"description": "Any known limitations or future improvements", "priority": "low|medium|high"}}
  ],
  "next_steps": "What the QA agent should focus on when testing"
}}
```

Remember:
- Implement complete, working code (no placeholders or TODOs)
- All code must be production-ready
- Follow SOLID principles and clean code practices
- Comprehensive test coverage
- Document all significant decisions
"""

    # Invoke AI API based on provider
    try:
        if AI_PROVIDER == "gemini":
            result = _invoke_gemini(system_prompt, user_prompt)
        else:
            result = _invoke_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        print(f"Error invoking Dev Agent: {e}", file=sys.stderr)
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
        error_file = f"dev_agent_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"Full response saved to {error_file}", file=sys.stderr)
        
        # Show context around the error
        if hasattr(e, 'pos') and e.pos:
            start = max(0, e.pos - 200)
            end = min(len(response_text), e.pos + 200)
            print(f"\nContext around error position:", file=sys.stderr)
            print(f"...{response_text[start:end]}...", file=sys.stderr)
        
        print(f"\nTip: Gemini may have generated invalid JSON. Check the error file for details.", file=sys.stderr)
        raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python invoke_dev_agent.py <feature_id>")
        sys.exit(1)
    
    feature_id = sys.argv[1]
    
    print(f"💻 Invoking Dev Agent for feature: {feature_id}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🤖 Provider: {AI_PROVIDER.upper()}")
    print(f"🤖 Model: {MODEL}")
    print()
    
    # Invoke the agent
    try:
        result = invoke_dev_agent(feature_id)
    except Exception as e:
        print(f"❌ Failed to invoke Dev Agent: {e}")
        sys.exit(1)
    
    print(f"✅ Dev Agent execution complete!")
    print(f"\nImplementation Summary:")
    print(result.get('implementation_summary', 'No summary provided'))
    
    # Create all files
    for file_info in result.get('files_created', []):
        filepath = REPO_ROOT / file_info['path']
        save_file(filepath, file_info['content'])
        print(f"  ✓ Created: {file_info['path']}")
    
    # Create all tests
    for test_info in result.get('tests_created', []):
        filepath = REPO_ROOT / test_info['path']
        save_file(filepath, test_info['content'])
        print(f"  ✓ Created test: {test_info['path']}")
    
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
        print(f"\n⚠️  Technical Debt Noted:")
        for debt in result['technical_debt']:
            print(f"  - [{debt['priority'].upper()}] {debt['description']}")
    
    print(f"\n🔜 Next Steps for QA:")
    print(f"  {result.get('next_steps', 'Standard QA testing')}")


if __name__ == "__main__":
    main()
