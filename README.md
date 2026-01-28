# AID: AI-Driven Development System

This repository is the single source of truth for:

- Product decisions
- Design intent
- Engineering changes
- Operational history

**No undocumented changes.**  
**No implicit decisions.**  
**Everything ties back to a belief.**

---

## Sequential Agent Pipeline

This system orchestrates 5 specialized agents in a sequential workflow:

```
Founder Input → Product → Design → Dev → QA → Ops → Deployed
```

### How It Works

1. **Founder** creates feedback/problem → `product/feedback/inbox.md`
2. **Product Agent** analyzes → creates belief/experiment → `product/decisions/`
3. **Design Agent** translates → creates intent/spec → `design/intents/`, `design/specs/`
4. **Dev Agent** implements → creates PR with code → behind feature flag
5. **QA Agent** validates → confirms intent match → `design/validations/`
6. **Ops Agent** deploys → gradual rollout → monitors

Each stage **must complete** before the next begins. State tracked in `.ai/pipeline/<feature-id>.state`

### Quick Start

```bash
# Start new feature pipeline
gh workflow run pipeline.yml -f feature_id=my-feature -f stage=intake

# Check pipeline status
cat .ai/pipeline/my-feature.state

# Continue to next stage
gh workflow run pipeline.yml -f feature_id=my-feature
```

---

## Documentation

- [Pipeline Architecture](.ai/PIPELINE.md) - Stage definitions and handoff rules
- [Orchestrator](.ai/workflows/pipeline-orchestrator.md) - Coordination logic
- [Agents](.ai/agents/) - Individual agent responsibilities

---

## Principles

- **Belief-driven**: Every change tests a hypothesis
- **Minimal scope**: Smallest reversible change
- **Sequential**: No skipping stages
- **Single-threaded**: One experiment at a time
