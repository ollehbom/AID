# Agent Pipeline Architecture

## Sequential Workflow

This system implements a **single-direction pipeline** where each agent produces artifacts for the next:

```
Founder Input → Product → Design (conditional) → Architect → Dev → QA → Ops → Deployed
```

**Key Flow Logic:**

- Product Agent decides if Design stage is needed (UI/UX changes)
- Architect Agent always runs before Dev (validates technical approach)
- All changes go through Architecture review regardless of Design involvement

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

### Stage 2: Design Intent (Conditional)

**Trigger**: Product agent completes experiment proposal AND sets `needs_design: true`  
**Agent**: Design Agent  
**Input**: `experiments/active.md` + `product/beliefs/current.md`  
**Outputs**:

- `design/intents/<feature-id>.md`
- `design/specs/<feature-id>.md`

**Exit Criteria**: Spec ready with flow, states, and copy tone defined

**Skipped When**: Product Agent determines change is purely technical (no UI/UX impact)

---

### Stage 3: Architecture Review

**Trigger**: Product agent completes OR Design spec completed  
**Agent**: Architect Agent  
**Input**:

- `product/decisions/<feature-id>.md`
- `design/specs/<feature-id>.md` (if design stage ran)
- `experiments/active.md`

**Outputs**:

- `design/architecture/ADR-<number>-<feature-id>.md` (Architecture Decision Record)
- `design/technical-specs/<feature-id>.md` (Technical specification)
- Updated pipeline state with architecture review

**Exit Criteria**:

- ADR documenting key architectural decisions
- Technical spec with implementation guidance
- Security, scalability, and reliability considerations addressed

**Focus Areas**:

- Well-Architected Framework (security, reliability, performance, cost)
- AI/ML-specific concerns (model fallbacks, orchestration)
- Database and infrastructure decisions
- Testing and deployment strategies

---

### Stage 3: Architecture Review

**Trigger**: Product agent completes OR Design spec completed  
**Agent**: Architect Agent  
**Input**:

- `product/decisions/<feature-id>.md`
- `design/specs/<feature-id>.md` (if design stage ran)
- `experiments/active.md`

**Outputs**:

- `design/architecture/ADR-<number>-<feature-id>.md` (Architecture Decision Record)
- `design/technical-specs/<feature-id>.md` (Technical specification)
- Updated pipeline state with architecture review

**Exit Criteria**:

- ADR documenting key architectural decisions
- Technical spec with implementation guidance
- Security, scalability, and reliability considerations addressed

**Focus Areas**:

- Well-Architected Framework (security, reliability, performance, cost)
- AI/ML-specific concerns (model fallbacks, orchestration)
- Database and infrastructure decisions
- Testing and deployment strategies

---

### Stage 4: Development

**Trigger**: Architect spec completed  
**Agent**: Dev Agent  
**Input**:

- `design/architecture/ADR-<number>-<feature-id>.md`
- `design/technical-specs/<feature-id>.md`
- `design/specs/<feature-id>.md` (if design stage ran)
- `engineering/architecture.md`

**Outputs**:

- Code changes (PR)
- `engineering/decisions/<id>.md` (if architecture changed)
- Updated experiment status in `experiments/active.md`

**Exit Criteria**: Feature implemented behind flag, tests pass

---

### Stage 5: QA Validation

**Trigger**: Dev PR merged  
**Agent**: QA Agent  
**Input**: Deployed code + `design/intents/<feature-id>.md`  
**Outputs**:

- `design/validations/<feature-id>.md`
- Test results
- Reversibility confirmation

**Exit Criteria**: Validation confirms intent match + reversibility verified

---

### Stage 6: Operations Rollout

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
status: architect_complete
needs_design: true
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  architect: ✓ 2026-01-29
  dev: in_progress
  qa: pending
  ops: pending
architecture:
  adr_number: ADR-042
  complexity: moderate
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
