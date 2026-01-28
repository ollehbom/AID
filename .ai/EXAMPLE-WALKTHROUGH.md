# Complete Pipeline Example: Onboarding Simplification

This document shows a complete walkthrough of a feature moving through all 5 stages.

---

## Stage 1: Founder Input → Product Agent

### Input

**File**: `product/feedback/inbox.md`

```markdown
### 2026-01-28 (Founder)

- Onboarding still feels heavy
- I hesitate before clicking "Create"

### 2026-01-27 (Early user)

- Unsure what happens after submit
```

### Product Agent Execution

```bash
gh workflow run pipeline.yml -f feature_id=onboarding-v2 -f stage=intake
```

**Agent reads**:

- `product/feedback/inbox.md` (raw feedback)
- `product/beliefs/current.md` (current hypothesis: "onboarding is intuitive")
- `.ai/workflows/decision-rules.md` (prioritization logic)

**Agent analyzes**:

- Pattern: Decision anxiety before first action
- Affected belief: "Onboarding is intuitive" (challenged)
- Founder intuition: Action before explanation

**Agent writes**:

- `product/decisions/2026-01-28-onboarding.md`
- Updates `experiments/active.md` with EXP-2026-01-ONBOARDING
- Creates `.ai/pipeline/onboarding-v2.state` (status: product_complete)

**State after**:

```yaml
feature: onboarding-v2
status: product_complete
stages:
  product: ✓ 2026-01-28
  design: pending
```

---

## Stage 2: Product → Design Agent

### Automatic Trigger

Pipeline detects `status: product_complete` → triggers Design Agent

### Design Agent Execution

**Agent reads**:

- `product/decisions/2026-01-28-onboarding.md`
- `experiments/active.md` (experiment: remove step 2, inline explanation)
- `product/beliefs/current.md` (must feel obvious)

**Agent creates intent**:
**File**: `design/intents/onboarding-v2.md`

```markdown
# Onboarding Simplification Intent

Problem: User hesitates before first action

Intent:

- Remove decision anxiety
- Make next step obvious
- Delay explanation until after action

Design Principles:

- One primary action
- No irreversible choices
- Immediate feedback

Non-goals:

- Teaching advanced concepts
- Full configuration
```

**Agent creates spec**:
**File**: `design/specs/onboarding-v2.md`

```markdown
# Onboarding v2 Spec

Flow:

1. Landing
2. Primary action CTA
3. Immediate system response
4. Contextual explanation (post-action)

Copy rules:

- No jargon
- No future promises
- Describe what just happened

Error handling:

- Inline, non-blocking
```

**Agent writes**:

- `design/intents/onboarding-v2.md`
- `design/specs/onboarding-v2.md`
- Updates `.ai/pipeline/onboarding-v2.state` (status: design_complete)

**State after**:

```yaml
status: design_complete
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  dev: pending
```

---

## Stage 3: Design → Dev Agent

### Automatic Trigger

Pipeline detects `status: design_complete` → triggers Dev Agent

### Dev Agent Execution

**Agent reads**:

- `design/specs/onboarding-v2.md` (what to build)
- `design/intents/onboarding-v2.md` (why)
- `engineering/architecture.md` (how: boring tech, easy rollback)
- `engineering/standards.md` (no abstraction without duplication)

**Agent implements**:

```javascript
// Feature flag: onboarding-v2
// Belief ref: product/decisions/2026-01-28-onboarding.md

if (featureFlags.onboardingV2) {
  // Skip step 2 (removed)
  showPrimaryAction();
  // Explanation inline after action (new)
  onActionComplete(() => showContextualExplanation());
} else {
  // Original flow (for rollback)
  showStep1();
  showStep2();
  showStep3();
}
```

**Agent writes**:

- Creates PR #123 with implementation
- Adds feature flag: `onboarding-v2` (default: off)
- Tests included
- Updates `.ai/pipeline/onboarding-v2.state` after PR merge (status: dev_complete)

**State after PR merge**:

```yaml
status: dev_complete
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  dev: ✓ 2026-01-30
  qa: pending
artifacts:
  dev: PR #123 merged
```

---

## Stage 4: Dev → QA Agent

### Automatic Trigger

Pipeline detects `status: dev_complete` + PR merged → triggers QA Agent

### QA Agent Execution

**Agent reads**:

- `design/intents/onboarding-v2.md` (expected: reduce hesitation)
- `design/specs/onboarding-v2.md` (expected behavior)
- `product/decisions/2026-01-28-onboarding.md` (success: no hesitation)
- Deployed code (with flag enabled in test env)

**Agent tests**:

1. **Intent match**: Does it reduce hesitation? ✓ Yes
2. **Unhappy paths**:
   - What if action fails? ✓ Inline error shown
   - What if no network? ✓ Graceful degradation
3. **Reversibility**:
   - Can feature flag disable? ✓ Yes
   - Does old flow still work? ✓ Yes
4. **Feel wrong?**: ✓ No confusion observed

**Agent writes**:
**File**: `design/validations/onboarding-v2.md`

```markdown
# Onboarding v2 Validation

Observed:

- Reduced hesitation ✓
- Faster first action ✓
- One moment of confusion post-action (explanation timing)

Assessment:

- Intent mostly met
- Explanation timing slightly late

Result: PASS (with minor note)

Reversibility: CONFIRMED

- Feature flag works
- Old flow intact
```

**Agent writes**:

- `design/validations/onboarding-v2.md`
- Updates `.ai/pipeline/onboarding-v2.state` (status: qa_complete)

**State after**:

```yaml
status: qa_complete
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  dev: ✓ 2026-01-30
  qa: ✓ 2026-01-31
  ops: pending
```

---

## Stage 5: QA → Ops Agent (Rollout)

### Automatic Trigger

Pipeline detects `status: qa_complete` → triggers Ops Agent

### Ops Agent Execution

**Agent reads**:

- `design/validations/onboarding-v2.md` (validation passed)
- Feature flag config (currently: off)
- `experiments/active.md` (experiment details)

**Agent plans**:

1. Enable for 10% users
2. Monitor for 24h
3. If stable → 50%
4. If stable → 100%
5. Rollback plan: disable flag

**Agent executes**:

```bash
# Day 1: 10%
feature-flag set onboarding-v2 --percentage=10

# Day 2: Check metrics
# No increase in errors ✓
# Hesitation reduced ✓
feature-flag set onboarding-v2 --percentage=50

# Day 3: Full rollout
feature-flag set onboarding-v2 --percentage=100
```

**Agent writes**:

- Deployment log
- Monitoring alerts configured
- Updates `.ai/pipeline/onboarding-v2.state` (status: deployed)
- Updates `experiments/active.md` (status: live)

**Final state**:

```yaml
status: deployed
completed: 2026-02-02
stages:
  product: ✓ 2026-01-28
  design: ✓ 2026-01-29
  dev: ✓ 2026-01-30
  qa: ✓ 2026-01-31
  ops: ✓ 2026-02-02
rollout:
  - 2026-02-01: 10% (stable)
  - 2026-02-02: 50% (stable)
  - 2026-02-02: 100% (deployed)
```

---

## Post-Deployment: Founder Evaluation

**2026-02-10** (1 week later)

Founder reviews:

- Success signal: "No hesitation during self-use" ✓ **MET**
- Side effects: Explanation timing slightly late (noted by QA)

**Decision**:

- Belief validated: Onboarding CAN be intuitive with action-first
- Update `product/beliefs/current.md`:
  - Move "Onboarding is intuitive" from "Open" to "Core"
- Archive experiment:
  - Move from `experiments/active.md` to `experiments/archive.md`

---

## Complete Timeline

| Date       | Stage | Agent   | Key Output                       |
| ---------- | ----- | ------- | -------------------------------- |
| 2026-01-28 | 1     | Product | Decision: EXP-2026-01-ONBOARDING |
| 2026-01-29 | 2     | Design  | Intent + Spec created            |
| 2026-01-30 | 3     | Dev     | PR #123 merged                   |
| 2026-01-31 | 4     | QA      | Validation: PASS                 |
| 2026-02-01 | 5     | Ops     | 10% rollout                      |
| 2026-02-02 | 5     | Ops     | 100% deployed                    |
| 2026-02-10 | -     | Founder | Belief validated ✓               |

**Total time**: 13 days (feedback → belief validated)

---

## Key Takeaways

✅ **Each stage had clear inputs/outputs**  
✅ **No stage was skipped**  
✅ **Reversibility maintained throughout**  
✅ **QA caught timing issue (Design can iterate)**  
✅ **Gradual rollout reduced risk**  
✅ **Belief validated through real usage**

This is belief-driven development in action. 🚀
