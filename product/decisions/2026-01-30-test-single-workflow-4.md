## Overview

This decision defines the initial experiment to establish the foundational React application with Google login and a basic dashboard, styled with shadcn/ui, to provide the first user touchpoint.

## Hypothesis

As a new user,
I believe a React application with a Google login and a basic dashboard (styled with shadcn/ui)
Will result in successful access to the product and an intuitive understanding of its basic structure
Because it aligns with modern web standards and design patterns, enabling further interaction and feature validation.

## Context

- **Affected Belief**: This experiment supports the existing beliefs: "The primary user is technically competent" and "The product must feel obvious without documentation." It also establishes a new foundational belief: "A modern React SPA with social login and a simple dashboard provides an intuitive initial user experience."
- **Current Workflow**: No application currently exists. Users cannot log in or access any product features.
- **Pain Point**: Inability to onboard new users or provide a basic product interface for internal testing and future feature development.
- **Success Metric**: 100% of internal testers successfully log in via Google and access the basic dashboard without issues.
- **Reversibility**: The deployment can be rolled back to a previous state, or the environment can be shut down. The application itself will be deployed to a staging environment initially.

## Acceptance Criteria

- [ ] React app initialized with shadcn/ui.
- [ ] Google OAuth login flow implemented and functional.
- [ ] Basic dashboard page with mock content accessible post-login.
- [ ] Experiment deployed to a test environment.
- [ ] Success metric tracked: successful logins and dashboard access.
- [ ] Rollback plan documented and understood.
- [ ] Results evaluated after 3 days of internal testing.

## Experiment Scope

- **Size**: `size: small`
- **Component**: `frontend`
- **Phase**: `phase-1-mvp`

## Definition of Done

- [ ] Feature flag configured (if applicable, for internal staging deployment)
- [ ] Code implemented per design spec (from Design Agent)
- [ ] Tests written (≥85% coverage for core components)
- [ ] Documentation updated (basic setup guide)
- [ ] QA validation passed (internal team)
- [ ] Gradual rollout plan ready (N/A for initial internal deployment)
- [ ] Success metric baseline captured (N/A, this is the baseline)

## Success Evaluation

- **Metric**: Percentage of internal testers successfully logging in and viewing the dashboard.
- **Target**: 100% successful logins and dashboard access by internal testers.
- **Measured via**: Manual testing and internal feedback.
- **Timeline**: Evaluate after 3 days of internal testing.
- **If successful**: Update belief to "Core" in product/beliefs/current.md: "A modern React SPA with social login and a simple dashboard provides an intuitive initial user experience."
- **If unsuccessful**: Archive in product/beliefs/history.md and document learnings, iterate on the initial user experience.

## Dependencies

- Blocked by: N/A
- Blocks: All subsequent feature development.
- Related belief: "The primary user is technically competent", "The product must feel obvious without documentation".

## Related Documentation

- Decision record: `product/decisions/test-single-workflow-4.md`
- Experiment tracking: `experiments/active.md`
- Design intent: `design/intents/test-single-workflow-4.md` (created by Design Agent)