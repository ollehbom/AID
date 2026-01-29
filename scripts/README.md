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

---

## Design Agent

**Script**: `invoke_design_agent.py`

Invokes the Design Agent using OpenAI GPT-4.1 or Google Gemini 2.5 Pro to create design intent, specifications, and wireframes.

### Prerequisites

```bash
# Install dependencies
pip install openai google-generativeai

# Set API key (choose one)
export OPENAI_API_KEY="your-openai-api-key"
# OR
export GOOGLE_API_KEY="your-google-api-key"

# Optional: Set provider and model
export AI_PROVIDER="openai"  # or "gemini"
export MODEL="gpt-4.1"  # or "gemini-2.0-flash-exp"
```

### Usage

```bash
# Basic usage
python scripts/invoke_design_agent.py feature-name

# With additional context
python scripts/invoke_design_agent.py onboarding-v2 "Focus on mobile-first design"
```

### What It Does

1. Reads Design Agent instructions from `.ai/agents/design.md`
2. Loads context files:
   - `product/decisions/<feature-id>.md` - Product decision
   - `experiments/active.md` - Active experiments
   - `product/beliefs/current.md` - Current beliefs
3. Invokes AI model with full context
4. Generates structured outputs:
   - Design intent document
   - Design specification
   - Wireframe JSON (structured layout)
   - Validation notes
5. Updates pipeline state to `design_complete`

### Output Files

- `design/intents/<feature-id>.md` - Why this exists and how it should feel
- `design/specs/<feature-id>.md` - Flow, states, copy, error handling
- `design/wireframes/<feature-id>.json` - Wireframe structure for dev agent
- `design/validations/<feature-id>.md` - Validation findings
- `.ai/pipeline/<feature-id>.state` - Updated pipeline state

### Environment Variables

- `OPENAI_API_KEY` or `GOOGLE_API_KEY` - Required. Your AI provider API key.
- `AI_PROVIDER` - Optional. "openai" or "gemini" (default: "openai")
- `MODEL` - Optional. Model name (default: "gpt-4.1")
- `TEMPERATURE` - Optional. Model temperature (default: "0.7")

### Error Handling

The script will exit with code 1 if:

- Missing feature_id argument
- Pipeline state file not found (product agent must run first)
- API key not set
- API call fails
- File write fails

---

## Future Agent Scripts

- `invoke_dev_agent.py` - Code implementation assistance
- `invoke_qa_agent.py` - Validation and testing
- `invoke_ops_agent.py` - Deployment orchestration
