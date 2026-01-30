# Agent Execution Scripts

This directory contains scripts for invoking AI agents in the pipeline.

## Overview

The AID pipeline uses multiple specialized agents:

- **Product Agent**: Analyzes feedback and creates product decisions
- **Design Agent**: Creates UX/UI specifications and wireframes
- **Architect Agent**: Reviews architecture and creates technical specs
- **Dev Agent**: Implements code based on specifications
- **Ops Agent**: Creates deployment and CI/CD configurations

## Utilities

- **json_fixer.py**: Automatic JSON error recovery for AI model responses
  - See [JSON-FIXER-README.md](JSON-FIXER-README.md) for details
  - Fixes common issues with Gemini-generated JSON (control characters, formatting, etc.)
  - Used by all agent scripts for robust JSON parsing

## Configuration

All agents support both OpenAI and Google Gemini:

```bash
# Install dependencies
pip install openai google-genai python-dotenv

# Set API keys in .env
OPENAI_API_KEY="your-openai-api-key"
GOOGLE_API_KEY="your-google-api-key"

# Configure provider and model
AI_PROVIDER="gemini"  # or "openai"
MODEL="gemini-2.5-flash"  # or "gpt-4.1"
TEMPERATURE="0.7"
```

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

## Architect Agent

**Script**: `invoke_architect_agent.py`

Invokes the Architect Agent to review architecture and create technical specifications.

### Usage

```bash
python scripts/invoke_architect_agent.py feature-name
```

### What It Does

1. Reads Architect Agent instructions from `.ai/agents/architect.md`
2. Loads context files:
   - Product decision
   - Design specs (if available)
   - Engineering standards
3. Generates Architecture Decision Records (ADRs)
4. Creates technical specifications
5. Updates pipeline state

### Output Files

- `design/architecture/ADR-<number>-<feature-id>.md` - Architecture decisions
- `design/technical-specs/<feature-id>.md` - Technical implementation guide

## Dev Agent

**Script**: `invoke_dev_agent.py`

Invokes the Dev Agent to implement production-ready code based on specifications.
Based on Software Engineer Agent v1 principles.

### Usage

```bash
python scripts/invoke_dev_agent.py feature-name
```

### What It Does

1. Reads technical specs and ADRs
2. Implements production-ready code following SOLID principles
3. Creates comprehensive test suite
4. Generates documentation
5. Validates quality gates

### Engineering Standards

- **SOLID principles** applied
- **Clean Code**: DRY, YAGNI, KISS
- **Testing**: Unit, integration, E2E tests
- **Security**: Secure-by-design
- **Documentation**: "Why" comments, API docs

### Output Files

- Implementation files (location based on technical spec)
- Test files
- Documentation updates
- Quality checklist report

## Ops Agent

**Script**: `invoke_ops_agent.py`

Invokes the Ops Agent to create deployment configurations and CI/CD updates.
Based on SE GitOps/CI Specialist principles.

### Usage

```bash
python scripts/invoke_ops_agent.py feature-name
```

### What It Does

1. Reads technical specs and implementation
2. Creates CI/CD pipeline configurations
3. Sets up monitoring and alerting
4. Generates deployment runbooks
5. Configures security and secrets management

### Operations Focus

- **Reliability**: Safe, predictable deployments
- **Automation**: Eliminate manual steps
- **Monitoring**: Health checks and alerts
- **Recovery**: Rollback procedures ready

### Output Files

- `.github/workflows/*.yml` - CI/CD pipeline updates
- `.env.example` - Environment variable template
- `docs/deployment.md` - Deployment runbook
- Monitoring configuration
- Security documentation

## Error Handling

All agents include robust error handling:

- JSON parsing errors save full response to timestamped files
- Context around errors shown for debugging
- Gemini responses automatically cleaned of markdown wrapping
- Detailed error messages for troubleshooting

## Pipeline Integration

These scripts are invoked by GitHub Actions workflows:

- `product-agent.yml` → `invoke_product_agent.py`
- `design-agent.yml` → `invoke_design_agent.py`
- `architect-agent.yml` → `invoke_architect_agent.py`
- `dev-agent.yml` → `invoke_dev_agent.py`
- `ops-agent.yml` → `invoke_ops_agent.py`

See [PIPELINE-WORKFLOW.md](../PIPELINE-WORKFLOW.md) for complete pipeline documentation.

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
