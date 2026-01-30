## Overview

Establish a foundational React application with Google login and a basic dashboard, integrating shadcn/ui as the core design system to enable initial user interaction and future UI development.

## Hypothesis

As a technical founder/early user
I believe that providing a basic React application with a login, a dashboard, and a consistent design system (shadcn/ui)
Will result in enabled initial product interaction, accelerated feedback loops, and validated need for a graphical user interface.
Because we currently lack a user-facing application to demonstrate core value and gather UI feedback.

## Context

- **Affected Belief**: This initiative supports the core belief that "The product must feel obvious without documentation" by establishing a well-designed UI foundation, and "Users value speed over configurability" by leveraging a modern UI library for rapid development. It also implicitly validates the need for a UI to test future product beliefs.
- **Current Workflow**: Currently, product interaction is primarily through non-graphical interfaces (e.g., command line, API).
- **Pain Point**: Lack of a visual interface hinders broader initial user testing, demonstration of product value, and rapid iteration on user experience.
- **Success Metric**: Successful Google login rate for internal users, ability to access a basic dashboard, and consistent application of shadcn/ui components.
- **Reversibility**: The core application can be re-architected or replaced if the chosen technology stack proves unsuitable, but the need for a UI will remain. Individual UI features will be implemented with feature flags later. This initial setup is additive.

## Acceptance Criteria

- [ ] React application scaffolded and deployed.
- [ ] Google OAuth login implemented and functional.
- [ ] Basic dashboard accessible post-login.
- [ ] shadcn/ui integrated and used for core UI components.
- [ ] Success metric tracked: Google login success rate (100% for internal testing).
- [ ] Rollback plan for specific features (not the base app) considered for future iterations.
- [ ] Results evaluated after initial internal deployment.

## Experiment Scope

- **Size**: `size: medium`
- **Component**: `frontend`
- **Phase**: `phase-1-mvp`

## Definition of Done

- [ ] React app repository initialized.
- [ ] Google OAuth configured and functional.
- [ ] Dashboard route and basic component created.
- [ ] shadcn/ui setup complete and used for login/dashboard elements.
- [ ] Initial tests written for login flow.
- [ ] Basic deployment pipeline established.
- [ ] Success metric baseline (0 users) captured.

## Success Evaluation

- **Metric**: Percentage of successful Google logins.
- **Target**: 100% successful logins for internal testers.
- **Measured via**: Internal testing and log analysis.
- **Timeline**: Evaluate after 1 week of internal testing.
- **If successful**: This foundational UI enables future experiments. Document learnings in product/beliefs/history.md about the effectiveness of shadcn/ui and Google login for initial setup.
- **If unsuccessful**: Analyze technical blockers with Google login or shadcn/ui integration, or usability issues with the basic dashboard. Iterate on the chosen technologies or approach.

## Dependencies

- Blocked by: None
- Blocks: All future UI-dependent features.
- Related belief: The need for a user-friendly UI to interact with the product.

## Related Documentation

- Decision record: `product/decisions/test-separate-pipelines-5.md` (this document)
- Experiment tracking: `experiments/active.md`
- Design intent: `design/intents/test-separate-pipelines-5.md` (will be created by Design Agent)
