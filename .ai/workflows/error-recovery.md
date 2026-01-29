# Automated Error Recovery System

The AID system includes an automated error recovery mechanism that detects pipeline failures, analyzes errors, and implements fixes autonomously.

## How It Works

### 1. Error Detection

When any workflow in the pipeline fails, the [auto-fix.yml](../.github/workflows/auto-fix.yml) workflow is automatically triggered via `workflow_run` event.

### 2. Issue Creation

The system:

- Downloads the failed workflow logs
- Extracts error messages and context
- Creates a GitHub issue with:
  - Error ID (timestamp-based)
  - Error logs
  - Workflow details
  - Agent task instructions

### 3. Automated Fix Pipeline

The [error-fix.yml](../.github/workflows/error-fix.yml) workflow is triggered with the error details and:

- Invokes the Error Recovery Agent
- Analyzes the error using AI
- Implements the minimal fix
- Creates a new branch
- Opens a PR with the fix
- Updates the issue with analysis

### 4. Validation & Merge

- Runs validation tests on the fix
- If tests pass, auto-merges the PR
- If tests fail, requests human review
- Updates the issue with results

## Error Recovery Agent

The [Error Recovery Agent](../agents/error-recovery.md) is an AI-powered agent that:

### Analyzes Errors

- Parses error logs
- Identifies error type (Syntax, Dependency, Config, Logic, Environment)
- Determines root cause
- Reads affected files

### Implements Fixes

- Generates minimal, targeted fixes
- Modifies only affected files
- Preserves code style and patterns
- Adds explanatory comments

### Documents Changes

- Creates detailed analysis reports
- Writes PR descriptions
- Updates issues with findings
- Provides validation steps

## Error Types Handled

### Syntax Errors

- Python syntax errors
- YAML/JSON parsing errors
- String formatting issues
- Quote mismatches

**Example Fix:**

```python
# Before (error)
f"ID: {datetime.now().strftime('%Y-%m-%d')}"

# After (fixed)
f"ID: {datetime.now().strftime('%Y-%m-%d')}"
```

### Dependency Issues

- Missing imports
- Package not installed
- Version conflicts

**Example Fix:**

```diff
# requirements.txt
openai==1.12.0
+ google-generativeai==0.3.2
```

### Configuration Errors

- Missing environment variables
- Invalid config values
- Wrong file paths

**Example Fix:**

```yaml
# Before
GOOGLE_API_KEY: ${{ secrets.GEMINI_API_KEY }}

# After
GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

### Logic Errors

- Incorrect conditionals
- Wrong variable usage
- API misuse

### Environment Issues

- Missing permissions
- File not found
- Directory creation needed

## Workflow Triggers

### Automatic Trigger

```yaml
on:
  workflow_run:
    workflows: ["Pipeline Orchestrator"]
    types: [completed]
```

Any time a workflow completes with failure status, auto-fix kicks in.

### Manual Trigger

You can also manually trigger error recovery:

```bash
gh workflow run error-fix.yml \
  -f error_id="error-20260129-153045" \
  -f issue_number="42"
```

## Output Structure

### Generated Files

```
.ai/error-fixes/
├── {error_id}-analysis.json       # Full error analysis
├── {error_id}-issue-update.md     # Issue comment content
└── {error_id}-pr-description.md   # PR description
```

### Analysis JSON Structure

```json
{
  "analysis": {
    "error_type": "Syntax",
    "root_cause": "F-string quote mismatch",
    "affected_files": ["scripts/invoke_product_agent.py"],
    "line_numbers": [135]
  },
  "fix": {
    "description": "Changed inner quotes from single to double",
    "files_to_modify": [
      {
        "path": "scripts/invoke_product_agent.py",
        "changes": "Fixed f-string quotes",
        "new_content": "... full file content ..."
      }
    ]
  },
  "validation": {
    "tests_to_run": ["python -m py_compile scripts/*.py"],
    "expected_outcome": "No syntax errors"
  }
}
```

## Success Criteria

✅ Error correctly identified and classified  
✅ Minimal fix implemented  
✅ No unrelated changes  
✅ Fix properly documented  
✅ Tests pass after fix  
✅ PR auto-merged if validated

## Limitations

The agent cannot automatically fix:

- Complex architectural issues
- Multi-file refactorings
- Database migrations
- External API changes

For these cases, the agent:

- Documents the analysis
- Provides manual fix instructions
- Tags issue with `needs-human-review`
- Assigns to appropriate team

## Configuration

Set these secrets in your GitHub repository:

```bash
OPENAI_API_KEY      # or
GOOGLE_API_KEY      # depending on AI_PROVIDER
AI_PROVIDER         # "openai" or "gemini"
MODEL               # e.g., "gpt-4.1" or "gemini-2.5-pro"
```

## Monitoring

Track error recovery effectiveness:

- Check issues with label `pipeline-error`
- Review PRs with label `auto-fix`
- Monitor fix success rate
- Review validation failures

## Best Practices

1. **Keep errors atomic**: Each workflow should fail for one clear reason
2. **Clear error messages**: Ensure errors have good traceback and context
3. **Review first fixes**: Human-review first few auto-fixes to validate behavior
4. **Monitor patterns**: If same error repeats, address root cause
5. **Update agent**: Improve agent instructions based on failure patterns

## Example Flow

```
Pipeline fails
    ↓
auto-fix.yml detects failure
    ↓
Downloads error logs
    ↓
Creates issue #123 with error details
    ↓
Triggers error-fix.yml
    ↓
Error Recovery Agent analyzes
    ↓
Generates fix for scripts/file.py
    ↓
Creates branch fix/error-20260129
    ↓
Commits and pushes fix
    ↓
Opens PR #124
    ↓
Updates issue #123 with analysis
    ↓
Runs validation tests
    ↓
Tests pass → Auto-merge PR
    ↓
Closes issue #123
    ↓
Pipeline runs successfully ✓
```

## Extending the System

### Add New Error Type

1. Update [error-recovery.md](../agents/error-recovery.md) with new classification
2. Add examples and fix strategies
3. Update agent prompt with patterns to recognize

### Custom Validation

Modify `error-fix.yml` validation step:

```yaml
- name: Run validation tests
  run: |
    # Add custom validation commands
    python -m pytest tests/
    npm run lint
    ./scripts/validate-config.sh
```

### Integration with Other Workflows

Add `workflow_run` triggers for other workflows:

```yaml
on:
  workflow_run:
    workflows: ["Pipeline Orchestrator", "Build & Test", "Deploy"]
    types: [completed]
```
