# Example State File

This directory contains pipeline state files that track the progress of features through the agent workflow.

## State File Format

Each file is named `<feature-id>.state` and contains:

```yaml
feature: feature-name
status: current_stage
stages:
  product: ✓ 2026-01-28 | pending | blocked
  design: ✓ 2026-01-29 | pending | blocked
  dev: in_progress | pending | blocked
  qa: pending
  ops: pending
```

## Valid Statuses

- `intake` - Waiting for Product Agent
- `product_complete` - Product analysis done, ready for Design
- `design_complete` - Design spec ready, ready for Dev
- `dev_complete` - Implementation done, ready for QA
- `qa_complete` - Validation passed, ready for Ops
- `deployed` - Feature live in production
- `blocked` - Issue requiring founder intervention

## Example

See `example-onboarding-v2.state` for reference.
