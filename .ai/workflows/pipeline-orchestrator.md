# Pipeline Orchestrator

## Purpose

Orchestrates the sequential execution of agents in the belief-driven development pipeline.

## Flow

```
INPUT (Founder)
    ↓
[Product Agent] → belief/experiment
    ↓
[Design Agent] → intent/spec
    ↓
[Dev Agent] → implementation
    ↓
[QA Agent] → validation
    ↓
[Ops Agent] → deployment
    ↓
OUTPUT (Live Feature)
```

## Commands

### Start New Feature

```bash
npm run pipeline:start -- --input="Founder note: onboarding is confusing"
```

Creates:

- `product/decisions/2026-01-28-onboarding.md`
- `.ai/pipeline/onboarding-v2.state`
- Triggers Product Agent

### Continue Pipeline

```bash
npm run pipeline:continue
```

Reads state file, determines next stage, triggers appropriate agent.

### Pipeline Status

```bash
npm run pipeline:status
```

Shows current stage and blocking issues.

## State Transitions

States stored in `.ai/pipeline/<feature-id>.state`

**Valid transitions:**

- `intake` → `product_complete`
- `product_complete` → `design_complete`
- `design_complete` → `dev_complete`
- `dev_complete` → `qa_complete`
- `qa_complete` → `ops_complete`
- `ops_complete` → `deployed`

**Rollback transitions:**

- `qa_complete` → `dev_complete` (if validation fails)
- Any stage → `blocked` (with reason)

## Agent Triggers

### Product Agent

**When**: New input in `product/feedback/inbox.md` or state = `intake`  
**Reads**:

- `product/feedback/inbox.md`
- `product/beliefs/current.md`
  **Writes**:
- `product/decisions/<id>.md`
- `experiments/active.md`
- Updates state to `product_complete`

### Design Agent

**When**: State = `product_complete`  
**Reads**:

- `experiments/active.md`
- `product/beliefs/current.md`
- `product/decisions/<id>.md`
  **Writes**:
- `design/intents/<feature-id>.md`
- `design/specs/<feature-id>.md`
- `design/wireframes/<feature-id>.json`
- `design/validations/<feature-id>.md`
- Updates state to `design_complete`

**Execution**:

```bash
python scripts/invoke_design_agent.py <feature-id>
```

### Dev Agent

**When**: State = `design_complete`  
**Reads**:

- `design/specs/<feature-id>.md`
- `engineering/architecture.md`
- `engineering/standards.md`
  **Writes**:
- Code (via PR)
- `engineering/decisions/<id>.md` (if needed)
- Updates state to `dev_complete`

### QA Agent

**When**: State = `dev_complete` AND PR merged  
**Reads**:

- `design/intents/<feature-id>.md`
- `design/specs/<feature-id>.md`
- Deployed code
  **Writes**:
- `design/validations/<feature-id>.md`
- Updates state to `qa_complete` OR `blocked`

### Ops Agent

**When**: State = `qa_complete`  
**Reads**:

- `design/validations/<feature-id>.md`
- Feature flag configuration
  **Writes**:
- Rollout plan
- Monitoring configuration
- Updates state to `ops_complete` → `deployed`

## Implementation

See `.github/workflows/pipeline.yml` for GitHub Actions orchestration.
