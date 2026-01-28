# Product Agent Quick Start

## What It Does

The Product Agent analyzes feedback and converts it into testable experiments using GPT-4.1.

**Input**: Raw feedback from founders/users  
**Output**: Structured decision records, experiments, and GitHub issues

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy and edit .env file
cp .env.example .env
nano .env  # Add your OpenAI API key
```

### 3. Add Feedback

```bash
echo "### 2026-01-28 (Founder)
- Feature X is confusing
- Users hesitate before clicking" >> product/feedback/inbox.md
```

### 4. Run Product Agent

```bash
python scripts/invoke_product_agent.py feature-x
```

### 5. Review Outputs

```bash
# Decision record
cat product/decisions/2026-01-28-feature-x.md

# Experiment
cat experiments/active.md

# GitHub issue (ready to create)
cat .ai/pipeline/feature-x-issue.md
```

## What You Get

### 1. Product Decision Record

Location: `product/decisions/<date>-<feature-id>.md`

Contains:

- **Hypothesis** - What belief is being tested
- **Context** - Current workflow, pain point, affected belief
- **Experiment Scope** - Minimal change to test hypothesis
- **Success Criteria** - Measurable outcomes
- **Reversibility** - How to rollback

### 2. Experiment Entry

Location: `experiments/active.md` (appended)

Contains:

- Experiment ID
- Belief being tested
- Change being made
- Owner
- Status
- Success signal

### 3. GitHub Issue

Location: `.ai/pipeline/<feature-id>-issue.md`

Contains:

- Complete issue with hypothesis format
- All required labels
- Acceptance criteria
- Definition of done
- Success evaluation plan

### 4. Updated Beliefs (if needed)

Location: `product/beliefs/current.md`

Updates beliefs based on analysis:

- Core beliefs validated
- Open beliefs challenged
- New beliefs added

## Example Output

**Input Feedback:**

```
Users confused by signup flow
```

**Output Decision Record:**

```markdown
## Hypothesis

As a new user
I believe simplifying signup to 2 steps
Will result in 30% more completions
Because decision anxiety blocks progress

## Experiment Scope

- Size: size: small (2 days)
- Change: Remove step 2, inline help after step 1
- Reversibility: Feature flag `signup-v2`

## Success Evaluation

- Metric: Signup completion rate
- Target: 30% increase from baseline
- Measured via: Analytics
- Timeline: 1 week after rollout
```

## Pipeline Integration

After Product Agent completes:

```bash
# Automatic in GitHub Actions
# Or manual continuation:
gh workflow run pipeline.yml -f feature_id=feature-x

# Next: Design Agent creates intent + spec
# Then: Dev Agent implements
# Then: QA Agent validates
# Then: Ops Agent deploys
```

## Customization

### Change Model

Edit `scripts/invoke_product_agent.py`:

```python
MODEL = "gpt-4.1"  # Change to gpt-4o, gpt-4-turbo, etc.
```

### Add Context

Pass additional context:

```bash
python scripts/invoke_product_agent.py feature-x "Urgent: blocking users"
```

### Adjust Temperature

Edit for more/less creativity:

```python
temperature=0.7  # Lower = more focused, Higher = more creative
```

## Common Patterns

### Pattern 1: Feedback → Experiment

```bash
# Add feedback
echo "Feature X confuses users" >> product/feedback/inbox.md

# Generate experiment
python scripts/invoke_product_agent.py feature-x

# Review and approve
cat product/decisions/*.md
```

### Pattern 2: Belief Validation

```bash
# Test a specific belief
python scripts/invoke_product_agent.py onboarding \
  "Testing belief: Users prefer action before explanation"

# Check belief updates
cat product/beliefs/current.md
```

### Pattern 3: Multiple Feedbacks

```bash
# Collect feedback over time in inbox
# Then batch process:
python scripts/invoke_product_agent.py week-23-batch

# Agent synthesizes patterns across all feedback
```

## Troubleshooting

### "No feedback to analyze"

- Check `product/feedback/inbox.md` has content
- Ensure file exists and is readable

### "API rate limit exceeded"

- Wait a few minutes
- Check your OpenAI account usage
- Consider using gpt-4o-mini for testing

### "Invalid JSON response"

- Agent might have generated malformed output
- Check OpenAI status page
- Try running again (GPT-4.1 is usually reliable)

### Output doesn't match beliefs

- Review `product/beliefs/current.md` for accuracy
- Update beliefs if they're outdated
- Agent uses beliefs as context for decisions

## Best Practices

✅ **DO:**

- Keep feedback raw and unfiltered in inbox
- Run agent after accumulating 3-5 feedback items
- Review generated outputs before committing
- Update beliefs based on learnings
- Keep experiments small and reversible

❌ **DON'T:**

- Don't pre-filter or "clean up" feedback
- Don't run for trivial issues (use founder intuition)
- Don't skip reviewing outputs
- Don't let beliefs get stale
- Don't make experiments too large

## Next Steps

1. ✅ Test locally with sample feedback
2. ✅ Review generated decision record
3. ✅ Create GitHub issue from output
4. ✅ Set up GitHub Actions secret
5. 🔄 Run full pipeline
6. 🔄 Evaluate experiment results
7. 🔄 Update beliefs based on learnings

## Questions?

- Architecture: See [.ai/PIPELINE.md](.ai/PIPELINE.md)
- Full setup: See [SETUP.md](SETUP.md)
- Agent details: See [.ai/agents/product.md](.ai/agents/product.md)
- Examples: See [.ai/EXAMPLE-WALKTHROUGH.md](.ai/EXAMPLE-WALKTHROUGH.md)
