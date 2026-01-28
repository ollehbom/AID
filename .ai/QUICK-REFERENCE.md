# AID Pipeline Quick Reference

## The 5 Stages

```
1. PRODUCT → Decision + Experiment
2. DESIGN  → Intent + Spec
3. DEV     → Implementation + PR
4. QA      → Validation + Reversibility
5. OPS     → Deployment + Monitoring
```

## Commands

```bash
# Start pipeline
gh workflow run pipeline.yml -f feature_id=my-feature

# Check status
cat .ai/pipeline/my-feature.state

# View agent outputs
ls product/decisions/      # Product stage
ls design/intents/         # Design stage
ls design/specs/           # Design stage
git log                    # Dev stage (PRs)
ls design/validations/     # QA stage
```

## Stage Checklist

### ✓ Product Complete

- [ ] Decision record in `product/decisions/`
- [ ] Experiment in `experiments/active.md`
- [ ] Belief referenced
- [ ] Success signal defined
- [ ] State: `product_complete`

### ✓ Design Complete

- [ ] Intent doc in `design/intents/`
- [ ] Spec doc in `design/specs/`
- [ ] Flows defined
- [ ] Copy tone clear
- [ ] State: `design_complete`

### ✓ Dev Complete

- [ ] PR merged
- [ ] Feature flag added
- [ ] Tests pass
- [ ] Belief referenced in commit
- [ ] State: `dev_complete`

### ✓ QA Complete

- [ ] Validation in `design/validations/`
- [ ] Intent match confirmed
- [ ] Reversibility tested
- [ ] Result: PASS or BLOCKED
- [ ] State: `qa_complete` or back to `dev_complete`

### ✓ Ops Complete

- [ ] Gradual rollout planned
- [ ] Monitoring configured
- [ ] Rollback tested
- [ ] Feature live
- [ ] State: `deployed`

## File Locations

| Agent   | Reads                                                       | Writes                                                 |
| ------- | ----------------------------------------------------------- | ------------------------------------------------------ |
| Product | `product/feedback/inbox.md`<br>`product/beliefs/current.md` | `product/decisions/<id>.md`<br>`experiments/active.md` |
| Design  | `product/decisions/<id>.md`<br>`experiments/active.md`      | `design/intents/<id>.md`<br>`design/specs/<id>.md`     |
| Dev     | `design/specs/<id>.md`<br>`engineering/standards.md`        | Code (PR)<br>`engineering/decisions/<id>.md`           |
| QA      | `design/intents/<id>.md`<br>`design/specs/<id>.md`          | `design/validations/<id>.md`                           |
| Ops     | `design/validations/<id>.md`<br>Feature flag config         | Deployment logs<br>Monitoring config                   |

## State File Format

```yaml
feature: my-feature
status: design_complete # or: intake, product_complete, etc.
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  dev: in_progress
  qa: pending
  ops: pending
```

## Principles

- **One at a time**: Single active experiment
- **No skipping**: Must complete each stage
- **Belief-driven**: Every change tests hypothesis
- **Reversible**: Feature flags enable rollback
- **Minimal**: Smallest viable change

## When Things Block

| Issue              | Action               |
| ------------------ | -------------------- |
| Unclear experiment | Return to Product    |
| Ambiguous intent   | Clarify with Design  |
| Too complex        | Reduce scope at Dev  |
| Validation fails   | Fix at Dev           |
| Deploy risk high   | Adjust Ops rollout % |

## Documentation

- Full architecture: `.ai/PIPELINE.md`
- Complete example: `.ai/EXAMPLE-WALKTHROUGH.md`
- Agent details: `.ai/agents/*.md`
