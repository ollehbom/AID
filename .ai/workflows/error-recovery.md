# Automated Error Recovery System

The AID system includes an automated error recovery mechanism that detects pipeline failures, analyzes errors, and implements fixes autonomously.

## Safety Features

### Daily Rate Limit

To protect against excessive API usage and model provider rate limits, the auto-fix pipeline has a **maximum of 100 runs per day** (UTC timezone).

- If the limit is reached, a warning issue is created
- Auto-fix will resume the next day
- The limit can be adjusted in [auto-fix.yml](../.github/workflows/auto-fix.yml) (`MAX_DAILY_RUNS`)

## How It Works

### 1. Error Detection

When any workflow in the pipeline fails, the [auto-fix.yml](../.github/workflows/auto-fix.yml) workflow is automatically triggered via `workflow_run` event.

**Rate Limit Check**: Before proceeding, the system checks if the daily limit has been reached by counting auto-fix issues created today.

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
- Waits for all PR checks to complete (up to 5 minutes)
- If all checks pass:
  - **Auto-merges the PR to main**
  - Deletes the fix branch
  - Updates issue with success status
- If checks fail:
  - Requests human review
  - Adds `needs-review` label to issue

### 5. Automatic Pipeline Re-trigger

After successful merge to main:

- Identifies the workflow that originally failed
- Automatically triggers that workflow (or full pipeline if needed)
- Updates the issue with re-trigger status
- Monitors the re-run for success

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
    workflows:
      [
        "Pipeline Orchestrator",
        "Product Agent",
        "Design Agent",
        "Architect Agent",
        "Dev Agent",
        "QA Agent",
        "Ops Agent",
        "Stage Router",
      ]
    types: [completed]
```

Any time a workflow completes with failure status, auto-fix kicks in and monitors all main pipeline workflows.

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
✅ PR auto-merged to main if all checks pass  
✅ Original workflow re-triggered automatically after merge  
✅ Pipeline succeeds on retry

## Limitations

### Technical Limitations

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

### Rate Limit Protection

To prevent excessive API usage and costs:

- **Maximum 100 auto-fix runs per day** (configurable)
- Limit resets at midnight UTC
- When limit is reached:
  - A warning issue is created with details
  - Auto-fix is skipped for remaining failures
  - Manual intervention required or wait until next day
- Helps identify recurring issues that need permanent fixes

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
- **Watch for `rate-limit` issues**: Indicates daily limit reached

## Best Practices

1. **Keep errors atomic**: Each workflow should fail for one clear reason
2. **Clear error messages**: Ensure errors have good traceback and context
3. **Review first fixes**: Human-review first few auto-fixes to validate behavior
4. **Monitor patterns**: If same error repeats, address root cause
5. **Check rate limit usage**: If hitting the daily limit frequently, investigate recurring failures
6. **Adjust limit if needed**: Edit `MAX_DAILY_RUNS` in [auto-fix.yml](../.github/workflows/auto-fix.yml) if 100 is too restrictive
7. **Update agent**: Improve agent instructions based on failure patterns

## Example Flow

```
Pipeline fails (e.g., Dev Agent)
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
Opens PR #124 to main
    ↓
Updates issue #123 with analysis
    ↓
Runs validation tests
    ↓
Tests pass → Auto-merge PR to main
    ↓
Re-triggers failed workflow (Dev Agent)
    ↓
Workflow runs successfully ✓
    ↓
Closes issue #123
```

### Automatic Workflow Re-trigger

After a successful auto-fix merge, the system intelligently determines which workflow to re-run:

1. **Specific Stage Fix**: If a specific agent workflow failed (e.g., Dev Agent), that workflow is re-triggered
2. **Router Fix**: If Stage Router failed, it's re-triggered to continue the pipeline
3. **Orchestrator Fix**: If Pipeline Orchestrator failed, the full pipeline is re-run from the start
4. **Unknown/Complex**: Defaults to re-running the full pipeline orchestrator for safety

This ensures the pipeline automatically continues from where it failed after the fix is applied.

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
