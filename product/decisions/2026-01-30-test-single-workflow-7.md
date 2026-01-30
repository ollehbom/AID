## Overview

This experiment aims to establish a foundational user interface for the product, including a login system and a basic dashboard, styled with modern components. This is a critical step to enable user interaction and subsequent feature development.

## Hypothesis

As a **technical founder**
I believe **a basic, modern React application with Google login and a simple dashboard**
Will result in **the ability to quickly understand and begin interacting with the core product**
Because **a clear initial interface reduces friction to adoption and provides a platform for future features consistent with our 'obvious without documentation' belief.**

## Context

- **Affected Belief**: This work supports the core belief that "The product must feel obvious without documentation" by providing an intuitive starting point. It also aligns with "The primary user is technically competent" by using modern frameworks.
- **Current Workflow**: Currently, users (or the founder) lack a cohesive graphical interface to interact with the product's backend services, requiring direct API calls or command-line interactions.
- **Pain Point**: High friction for new users/founders to get started and understand the product's capabilities due to the absence of a user-friendly frontend. This also hinders early feedback collection on user experience.
- **Success Metric**: Successful deployment of the application, ability for internal users/founder to log in via Google, and successful navigation to a basic dashboard with mock content. Subsequent success will be measured by new user sign-ups and initial engagement metrics once released.
- **Reversibility**: The core application framework itself is not easily reversible via a feature flag. However, the *content* within the dashboard will be designed to be feature-flag ready. In case of critical issues, the deployment can be rolled back.

## Acceptance Criteria

- [ ] React application initialized with `shadcn/ui` for styling.
- [ ] Login screen implemented with Google authentication.
- [ ] Basic dashboard page accessible after successful login.
- [ ] Dashboard contains mock content (e.g., "Welcome, User!").
- [ ] Application deployed to a staging environment for internal review.

## Experiment Scope

- **Size**: `size: medium` (4-7 days)
- **Component**: `frontend`
- **Phase**: `phase-1-mvp`

## Definition of Done

- [ ] Feature flag configured (for future content, not core app)
- [ ] Code implemented per design spec
- [ ] Tests written (≥85% coverage for critical paths like login)
- [ ] Documentation updated (basic setup instructions)
- [ ] QA validation passed (internal founder review)
- [ ] Gradual rollout plan ready (initial internal, then controlled external)
- [ ] Success metric baseline captured (e.g., internal login success)

## Success Evaluation

- **Metric**: Internal founder validation of basic functionality and adherence to modern design standards. Subsequently, new user sign-ups and successful first login rates.
- **Target**: Founder approval of the initial UI. For user metrics, target will be set after initial deployment (e.g., 80% successful first logins for early adopters).
- **Measured via**: Direct founder feedback, internal testing, and later, analytics on login events.
- **Timeline**: Evaluate initial success within 1 week of deployment to staging.
- **If successful**: This establishes a core platform; it won't directly update a belief to "Core" but rather *supports* existing core beliefs. Further experiments will build upon this.
- **If unsuccessful**: Re-evaluate the approach to foundational UI, potentially simplifying or exploring alternative frameworks.

## Dependencies

- Blocked by: None
- Blocks: All future UI-dependent features.
- Related belief: `product/beliefs/current.md` (supports "product must feel obvious")

## Related Documentation

- Decision record: `product/decisions/test-single-workflow-7.md` (this document)
- Experiment tracking: `experiments/active.md`
- Design intent: `design/intents/test-single-workflow-7.md` (to be created by Design Agent)