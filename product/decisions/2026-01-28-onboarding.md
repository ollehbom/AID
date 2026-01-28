# Product Decision Record

**ID**: 2026-01-28-onboarding  
**Date**: 2026-01-28  
**Status**: Active Experiment  
**Belief**: Onboarding flow is intuitive without guidance

---

## Context

### Feedback

- Founder: "Onboarding still feels heavy"
- Founder: "I hesitate before clicking 'Create'"
- Early user: "Unsure what happens after submit"

### Affected Belief

Current belief states onboarding is intuitive, but repeated hesitation signals friction.

---

## Analysis

**Pattern identified**: Decision anxiety before first action

**Root cause hypothesis**: Too much information before action, not enough after

**Founder intuition**: Action should come first, explanation second

---

## Decision

### Experiment: EXP-2026-01-ONBOARDING

**Change**: Remove step 2, inline explanation after action  
**Scope**: Onboarding flow only  
**Reversibility**: Full (can restore step 2)  
**Success signal**: No hesitation during founder self-use

### Non-solutions rejected

- Adding more explanatory text (increases cognitive load)
- Tutorial mode (conflicts with "obvious" belief)
- Tooltips (defers problem)

---

## Next Steps

1. ✓ Product decision recorded
2. → Design agent creates intent + spec
3. → Dev implements behind flag
4. → QA validates reversibility
5. → Ops gradual rollout

---

## Outputs Created

- [x] This decision record
- [x] `experiments/active.md` updated
- [x] Pipeline state initialized

**Handoff to**: Design Agent
