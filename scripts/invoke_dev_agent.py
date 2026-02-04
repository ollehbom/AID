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
from json_fixer import parse_json_with_recovery
from pydantic import BaseModel
from typing import List, Dict, Any

# Load environment variables from .env file
load_dotenv()

# Pydantic Models for Schema Validation
class FileInfo(BaseModel):
    """Single file information."""
    path: str
    content: str
    description: str

class BuildCommands(BaseModel):
    """Build commands for the project."""
    install: str
    build: str
    test: str
    dev: str
    working_dir: str

class DevAgentResponse(BaseModel):
    """Type-safe response structure for Dev Agent."""
    implementation_files: List[FileInfo]
    test_files: List[FileInfo]
    build_commands: BuildCommands
    implementation_summary: str
    testing_summary: str
    next_steps: List[str]

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

Implement the feature according to the specifications above. 

**IMPORTANT**: This may be a greenfield project (no existing code). If the technical spec describes a new project, create the COMPLETE project structure including:
- All configuration files (package.json, tsconfig.json, .gitignore, etc.)
- All implementation files
- All test files
- README and documentation
- Build and development scripts

Create:

1. **Implementation Files**
   - Core implementation following the technical architecture
   - Proper error handling and edge cases
   - Security considerations implemented
   - Performance optimizations where specified
   - ALL necessary configuration files for the project

2. **Test Suite**
   - Unit tests for all core functionality
   - Integration tests for component interactions
   - Test edge cases and error conditions
   - Achieve comprehensive logical coverage
   - Test configuration files

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
  "implementation_files": [
    {{
      "path": "relative/path/to/file.py",
      "description": "Purpose of this file",
      "content": "Full file content"
    }}
  ],
  "test_files": [
    {{
      "path": "relative/path/to/test.py",
      "description": "What this test validates",
      "content": "Full test content"
    }}
  ],
  "build_commands": {{
    "install": "Command to install dependencies (e.g., 'npm install' or 'pip install -r requirements.txt')",
    "build": "Command to build the project (e.g., 'npm run build' or empty string if no build needed)",
    "test": "Command to run tests (e.g., 'npm test' or 'pytest')",
    "dev": "Command to run in development mode (e.g., 'npm run dev' or 'python app.py')",
    "working_dir": "Directory to run commands from (e.g., './' or 'client/' for monorepos)"
  }},
  "testing_summary": "Brief overview of test strategy and coverage",
  "next_steps": ["Step 1 for QA", "Step 2 for QA"]
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
    
    return parse_json_with_recovery(
        response.choices[0].message.content,
        error_prefix="dev_agent_error"
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
                response_schema=DevAgentResponse  # ✨ Schema validation!
            )
        )
        
        # Use validated, parsed response
        parsed = response.parsed
        
        # Convert Pydantic models to dicts
        impl_files = [{
            "path": f.path,
            "content": f.content,
            "description": f.description
        } for f in parsed.implementation_files]
        
        test_files = [{
            "path": f.path,
            "content": f.content,
            "description": f.description
        } for f in parsed.test_files]
        
        build_cmds = {
            "install": parsed.build_commands.install,
            "build": parsed.build_commands.build,
            "test": parsed.build_commands.test,
            "dev": parsed.build_commands.dev,
            "working_dir": parsed.build_commands.working_dir
        }
        
        return {
            "files_created": impl_files,
            "tests_created": test_files,
            "build_commands": build_cmds,
            "implementation_summary": parsed.implementation_summary,
            "testing_summary": parsed.testing_summary,
            "next_steps": parsed.next_steps
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
                error_prefix="dev_agent_error"
            )
        except Exception as fallback_error:
            raise Exception(f"Both schema validation and fallback failed: {e}, {fallback_error}")


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
    
    # Check if this is a recovered result
    if "_recovery_note" in result:
        print(f"⚠️  Warning: Partial recovery - some content may be incomplete")
        print(f"   {result['_recovery_note']}")
        print()
    
    print(f"✅ Dev Agent execution complete!")
    print(f"\nImplementation Summary:")
    print(result.get('implementation_summary', 'No summary provided'))
    
    # Validate that files were generated
    files_created = result.get('files_created', [])
    tests_created = result.get('tests_created', [])
    
    if not files_created and not tests_created:
        print(f"\n⚠️  WARNING: No files were generated!")
        print(f"   This usually means:")
        print(f"   1. JSON parsing failed (check error files)")
        print(f"   2. The agent didn't generate file content")
        print(f"   3. Recovery only captured summary fields")
        print(f"\n   Recommendation: Run again or switch to OpenAI (AI_PROVIDER=openai)")
        if "_recovery_note" not in result:
            sys.exit(1)
    
    # Create all files
    for file_info in files_created:
        filepath = REPO_ROOT / file_info['path']
        save_file(filepath, file_info['content'])
        print(f"  ✓ Created: {file_info['path']}")
    
    # Create all tests
    for test_info in tests_created:
        filepath = REPO_ROOT / test_info['path']
        save_file(filepath, test_info['content'])
        print(f"  ✓ Created test: {test_info['path']}")
    
    # Summary of created files
    if files_created or tests_created:
        print(f"\n📦 Generated {len(files_created)} implementation files and {len(tests_created)} test files")
    
    # Update documentation
    for doc_info in result.get('documentation_updates', []):
        filepath = REPO_ROOT / doc_info['path']
        save_file(filepath, doc_info['content'])
        print(f"  ✓ Updated docs: {doc_info['path']}")
    
    # Save build commands for pipeline automation
    if result.get('build_commands'):
        build_file = REPO_ROOT / ".ai/pipeline" / f"{feature_id}.build.json"
        save_file(build_file, json.dumps(result['build_commands'], indent=2))
        print(f"  ✓ Saved build commands: {build_file.relative_to(REPO_ROOT)}")
    
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
            # Handle both dict and string formats (from json_fixer fallback)
            if isinstance(debt, dict):
                priority = debt.get('priority', 'medium')
                description = debt.get('description', str(debt))
                print(f"  - [{priority.upper()}] {description}")
            else:
                print(f"  - {debt}")
    
    print(f"\n🔜 Next Steps for QA:")
    print(f"  {result.get('next_steps', 'Standard QA testing')}")


if __name__ == "__main__":
    main()
