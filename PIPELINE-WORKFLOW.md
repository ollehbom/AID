# PR-Based Pipeline Workflow

## Overview

The AID pipeline uses a PR-based approval workflow with **separate workflows for each stage**. Each agent creates a PR that requires human approval before the next stage automatically triggers.

## Workflow Files

- `product-agent.yml` - Analyzes feedback and creates product decisions
- `design-agent.yml` - Creates design specifications and wireframes
- `architect-agent.yml` - Reviews architecture and creates technical specs
- `dev-agent.yml` - Implements the feature (placeholder)
- `qa-agent.yml` - Validates implementation (placeholder)
- `ops-agent.yml` - Prepares deployment (placeholder)
- `stage-router.yml` - Automatically triggers next stage on PR merge

## How It Works

### 1. Start a New Feature

```bash
gh workflow run product-agent.yml -f feature_id=my-feature
```

This will:

- Create a feature branch: `feature/my-feature`
- Run the Product Agent
- Create a PR: `my-feature-product-stage` → `feature/my-feature`
- Wait for your approval

### 2. Review and Approve

1. Go to the PR created by the Product Agent
2. Review the outputs (decision record, experiment, etc.)
3. If approved: **Merge the PR**
4. If changes needed: Comment and close the PR (manual re-trigger needed)

### 3. Automatic Stage Progression

When you merge a stage PR:

- The `stage-router` workflow automatically triggers
- Updates pipeline state to mark stage as approved
- **Triggers the next stage workflow** based on the routing logic:
  - Product → Design (if needed) OR Architect
  - Design → Architect
  - Architect → Dev
  - Dev → QA
  - QA → Ops
  - Ops → Creates PR to `main`

**Key benefit:** Each stage runs as an independent workflow, giving you clear separation and the ability to re-run any stage independently.

### 4. Final Deployment

After Ops stage is approved:

- A final PR from `feature/my-feature` → `main` is created
- Review and merge this PR to deploy to production

## Stage Sequence

```
1. Product Agent    [PR Review] ✓
       ↓
2. Design Agent     [PR Review] ✓  (optional - if needs_design: true)
       ↓
3. Architect Agent  [PR Review] ✓
       ↓
4. Dev Agent        [PR Review] ✓
       ↓
5. QA Agent         [PR Review] ✓
       ↓
6. Ops Agent        [PR Review] ✓
       ↓
7. Deploy to Main   [PR Review] ✓
```

## Branch Structure

```
main
  └─ feature/my-feature (feature branch)
       ├─ my-feature-product-stage    (stage PR)
       ├─ my-feature-design-stage     (stage PR)
       ├─ my-feature-architect-stage  (stage PR)
       ├─ my-feature-dev-stage        (stage PR)
       ├─ my-feature-qa-stage         (stage PR)
       └─ my-feature-ops-stage        (stage PR)
```

## Manual Stage Triggers

If you need to manually trigger a specific stage:

```bash
# Trigger Product stage (start new feature)
gh workflow run product-agent.yml -f feature_id=my-feature

# Trigger Design stage
gh workflow run design-agent.yml -f feature_id=my-feature

# Trigger Architect stage
gh workflow run architect-agent.yml -f feature_id=my-feature

# Trigger Dev stage
gh workflow run dev-agent.yml -f feature_id=my-feature

# Trigger QA stage
gh workflow run qa-agent.yml -f feature_id=my-feature

# Trigger Ops stage
gh workflow run ops-agent.yml -f feature_id=my-feature
```

## Labels

Each PR is labeled for easy tracking:

- `stage:product` - Product Agent output
- `stage:design` - Design Agent output
- `stage:architect` - Architect Agent output
- `stage:dev` - Dev Agent output
- `stage:qa` - QA Agent output
- `stage:ops` - Ops Agent output
- `awaiting-approval` - Needs human review
- `deployment` - Final deployment PR
- `ready-to-merge` - All checks passed

## Example Flow

### Complete Walkthrough

1. **Start Product Stage:**

   ```bash
   gh workflow run pipeline.yml -f stage=product -f feature_id=checkout-redesign
   ```

2. **Product Agent runs, creates PR:**
   - PR: `checkout-redesign-product-stage` → `feature/checkout-redesign`
   - Review the product decision and experiment details

3. **Approve by merging the PR:**
   - Merge the PR in GitHub UI or: `gh pr merge <PR#>`

4. **Design Agent auto-triggers** (if `needs_design: true`):
   - New PR created automatically
   - Review design specs and wireframes

5. **Continue approving each stage:**
   - Each merge triggers the next stage
   - Review → Merge → Next stage (repeat)

6. **Final deployment:**
   - After Ops stage, PR to `main` is created
   - Merge this PR to deploy

## Troubleshooting

### Stage didn't auto-trigger after merge

Check the `stage-router` workflow run. If it failed, manually trigger:

```bash
gh workflow run pipeline.yml -f stage=<next-stage> -f feature_id=<feature-id>
```

### Need to restart a stage

Close the existing PR and re-trigger:

```bash
gh pr close <PR#>
gh workflow run pipeline.yml -f stage=<stage> -f feature_id=<feature-id>
```

### Check pipeline state

```bash
cat .ai/pipeline/<feature-id>.state
```

## Benefits

✅ **Human approval gates** - No stage proceeds without review  
✅ **Clear audit trail** - Each PR shows what changed  
✅ **Easy rollback** - Can revert any stage's changes  
✅ **Automatic progression** - Merge triggers next stage  
✅ **Flexible** - Can skip stages or manually trigger

## Next Steps

Try it out with a test feature:

```bash
gh workflow run pipeline.yml -f stage=product -f feature_id=test-feature
```
