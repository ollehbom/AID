# Agent Execution Scripts

This directory contains scripts for invoking AI agents in the pipeline.

## Product Agent

**Script**: `invoke_product_agent.py`

Invokes the Product Agent using OpenAI GPT-4.1 to analyze feedback and create experiments.

### Prerequisites

```bash
# Install dependencies
pip install openai

# Set API key
export OPENAI_API_KEY="your-openai-api-key"
```

### Usage

```bash
# Basic usage
python scripts/invoke_product_agent.py feature-name

# With additional context
python scripts/invoke_product_agent.py onboarding-v2 "Founder reported hesitation during signup"
```

### What It Does

1. Reads Product Agent instructions from `.ai/agents/product.md`
2. Loads context files:
   - `product/feedback/inbox.md`
   - `product/beliefs/current.md`
   - `.ai/workflows/decision-rules.md`
   - `.ai/workflows/change-intake.md`
3. Invokes GPT-4.1 with the full context
4. Generates structured outputs:
   - Product decision record
   - Experiment update
   - GitHub issue content
   - Belief updates (if needed)
5. Saves all outputs to appropriate files

### Output Files

- `product/decisions/<date>-<feature-id>.md` - Decision record
- `experiments/active.md` - Updated with new experiment
- `.ai/pipeline/<feature-id>-issue.md` - GitHub issue content
- `product/beliefs/current.md` - Updated beliefs (if changed)

### Environment Variables

- `OPENAI_API_KEY` - Required. Your OpenAI API key.

### Error Handling

The script will exit with code 1 if:

- Missing feature_id argument
- OPENAI_API_KEY not set
- API call fails
- File write fails

## Future Agent Scripts

- `invoke_design_agent.py` - Design intent and spec generation
- `invoke_dev_agent.py` - Code implementation assistance
- `invoke_qa_agent.py` - Validation and testing
- `invoke_ops_agent.py` - Deployment orchestration
