# Agent Pipeline Architecture

## Sequential Workflow

This system implements a **single-direction pipeline** where each agent produces artifacts for the next:

```
Founder Input → Product → Design → Dev → QA → Ops → Deployed
```

## Stage Definitions

### Stage 1: Product Analysis

**Trigger**: Founder creates issue or adds to feedback inbox  
**Agent**: Product Agent  
**Input**: `product/feedback/inbox.md` or GitHub issue  
**Outputs**:

- `product/beliefs/current.md` (updated)
- `experiments/active.md` (new experiment)
- `product/decisions/<id>.md` (decision record)

**Exit Criteria**: Experiment defined with clear success signal

---

### Stage 2: Design Intent

**Trigger**: Product agent completes experiment proposal  
**Agent**: Design Agent  
**Input**: `experiments/active.md` + `product/beliefs/current.md`  
**Outputs**:

- `design/intents/<feature-id>.md`
- `design/specs/<feature-id>.md`

**Exit Criteria**: Spec ready with flow, states, and copy tone defined

---

### Stage 3: Development

**Trigger**: Design spec completed  
**Agent**: Dev Agent  
**Input**: `design/specs/<feature-id>.md` + `engineering/architecture.md`  
**Outputs**:

- Code changes (PR)
- `engineering/decisions/<id>.md` (if architecture changed)
- Updated experiment status in `experiments/active.md`

**Exit Criteria**: Feature implemented behind flag, tests pass

---

### Stage 4: QA Validation

**Trigger**: Dev PR merged  
**Agent**: QA Agent  
**Input**: Deployed code + `design/intents/<feature-id>.md`  
**Outputs**:

- `design/validations/<feature-id>.md`
- Test results
- Reversibility confirmation

**Exit Criteria**: Validation confirms intent match + reversibility verified

---

### Stage 5: Operations Rollout

**Trigger**: QA validation passes  
**Agent**: Ops Agent  
**Input**: `design/validations/<feature-id>.md` + feature flag status  
**Outputs**:

- Gradual rollout plan
- Monitoring alerts configured
- `experiments/active.md` (status: live)

**Exit Criteria**: Feature live, rollback plan confirmed

---

## State Management

Each stage writes its completion state to track progress:

**File**: `.ai/pipeline/<feature-id>.state`

```yaml
feature: onboarding-v2
status: design_complete
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  dev: in_progress
  qa: pending
  ops: pending
```

## Handoff Rules

1. **No skipping stages** - Each agent must complete before next begins
2. **Blocking failures** - If QA fails, returns to Dev (not Design)
3. **Single active feature** - Only one experiment in pipeline at a time
4. **Artifact requirements** - Each stage must produce its outputs before handoff

## Agent Coordination

Agents coordinate via:

- **File system state** - Agents read/write to specific directories
- **GitHub workflows** - Orchestrate agent execution
- **Status files** - Track pipeline progress
