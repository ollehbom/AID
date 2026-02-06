"""
Dev Agent - AI-powered code generation with iterative refinement
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Choose AI provider
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')

if AI_PROVIDER == 'gemini':
    from google import genai
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
elif AI_PROVIDER == 'openai':
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

MODEL = os.getenv('MODEL', 'gemini-2.0-flash-exp')


class DevAgent:
    """AI agent for generating and fixing code."""
    
    def __init__(self, workspace: Path, feature_id: str):
        self.workspace = workspace
        self.feature_id = feature_id
        self.agent_instructions = self._load_agent_instructions()
    
    def _load_agent_instructions(self) -> str:
        """Load dev agent instructions."""
        agent_file = self.workspace / ".ai" / "agents" / "dev.md"
        if agent_file.exists():
            return agent_file.read_text()
        return "You are an expert software development agent."
    
    def _load_specs(self, design_spec_path: Path, arch_spec_path: Path) -> dict:
        """Load design and architecture specifications."""
        specs = {}
        
        if design_spec_path.exists():
            with open(design_spec_path) as f:
                specs['design'] = json.load(f)
        
        if arch_spec_path.exists():
            with open(arch_spec_path) as f:
                specs['architecture'] = json.load(f)
        
        # Also load markdown versions
        design_md = self.workspace / "design" / "specs" / f"{self.feature_id}.md"
        if design_md.exists():
            specs['design_md'] = design_md.read_text()
        
        arch_md = self.workspace / "design" / "technical-specs" / f"{self.feature_id}.md"
        if arch_md.exists():
            specs['architecture_md'] = arch_md.read_text()
        
        return specs
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call LLM with prompt."""
        if AI_PROVIDER == 'gemini':
            config = {'system_instruction': system_prompt or self.agent_instructions}
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=config
            )
            return response.text
        
        elif AI_PROVIDER == 'openai':
            messages = []
            if system_prompt or self.agent_instructions:
                messages.append({
                    'role': 'system',
                    'content': system_prompt or self.agent_instructions
                })
            messages.append({'role': 'user', 'content': prompt})
            
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            return response.choices[0].message.content
    
    def generate_implementation(self, design_spec_path: Path, arch_spec_path: Path):
        """Generate initial implementation from specifications."""
        logger.info("Generating implementation...")
        
        specs = self._load_specs(design_spec_path, arch_spec_path)
        
        prompt = f"""# Implementation Request

## Feature ID
{self.feature_id}

## Design Specification
{specs.get('design_md', 'Not available')}

## Technical Specification
{specs.get('architecture_md', 'Not available')}

---

Generate the complete implementation for this feature. Include:
1. All necessary source files
2. Configuration files (package.json, tsconfig.json, etc.)
3. Test files
4. Build commands in a .build.json file

For each file, provide:
- **Path**: Relative path from project root
- **Content**: Complete file content
- **Description**: What this file does

Format your response as JSON:

```json
{{
  "files": [
    {{
      "path": "src/example.ts",
      "content": "...",
      "description": "Example component"
    }}
  ],
  "build_commands": {{
    "install": "npm install",
    "build": "npm run build",
    "test": "npm test",
    "dev": "npm run dev",
    "working_dir": "./"
  }}
}}
```
"""
        
        response = self._call_llm(prompt)
        
        # Extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise Exception("No JSON found in LLM response")
        
        implementation = json.loads(response[json_start:json_end])
        
        # Write files
        for file_info in implementation.get('files', []):
            file_path = self.workspace / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Writing {file_path}")
            file_path.write_text(file_info['content'])
        
        # Write build commands
        build_file = self.workspace / ".ai" / "pipeline" / f"{self.feature_id}.build.json"
        build_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(build_file, 'w') as f:
            json.dump(implementation.get('build_commands', {}), f, indent=2)
        
        logger.info(f"Generated {len(implementation.get('files', []))} files")
        
        return implementation
    
    def fix_build_error(self, error_message: str) -> dict:
        """Analyze and fix a build error."""
        logger.info("Fixing build error...")
        
        prompt = f"""# Build Error Fix Request

## Feature ID
{self.feature_id}

## Error Message
```
{error_message}
```

## Task
Analyze this build error and provide a fix.

Common issues:
- Missing dependencies (add to package.json)
- Missing imports (add import statements)
- Type errors (fix TypeScript types)
- Configuration issues (update tsconfig.json, vite.config.ts)
- Missing scoped package prefixes (e.g., `react-router-dom` should be `@react-router-dom`)

Provide your fix as JSON:

```json
{{
  "analysis": "Brief explanation of the error",
  "fix_type": "dependency|code|config",
  "files": [
    {{
      "path": "path/to/file",
      "content": "Updated file content",
      "description": "What was fixed"
    }}
  ]
}}
```

Provide ONLY files that need changes, not the entire codebase.
"""
        
        response = self._call_llm(prompt)
        
        # Extract JSON
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            logger.error("No JSON in fix response")
            return {'success': False, 'error': 'No JSON in response'}
        
        fix = json.loads(response[json_start:json_end])
        
        # Apply fixes
        for file_info in fix.get('files', []):
            file_path = self.workspace / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Fixing {file_path}")
            file_path.write_text(file_info['content'])
        
        logger.info(f"Applied fix: {fix.get('analysis')}")
        
        return {'success': True, 'fix': fix}
    
    def fix_test_failures(self, error_message: str) -> dict:
        """Analyze and fix test failures."""
        logger.info("Fixing test failures...")
        
        prompt = f"""# Test Failure Fix Request

## Feature ID
{self.feature_id}

## Test Output
```
{error_message}
```

## Task
Analyze these test failures and provide fixes to make the tests pass.

Provide your fix as JSON:

```json
{{
  "analysis": "Brief explanation of failures",
  "files": [
    {{
      "path": "path/to/file",
      "content": "Updated content",
      "description": "What was fixed"
    }}
  ]
}}
```
"""
        
        response = self._call_llm(prompt)
        
        # Extract JSON
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            return {'success': False, 'error': 'No JSON in response'}
        
        fix = json.loads(response[json_start:json_end])
        
        # Apply fixes
        for file_info in fix.get('files', []):
            file_path = self.workspace / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Fixing {file_path}")
            file_path.write_text(file_info['content'])
        
        logger.info(f"Applied test fix: {fix.get('analysis')}")
        
        return {'success': True, 'fix': fix}
