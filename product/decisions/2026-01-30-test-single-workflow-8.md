# Decision Record: Establish Core React Application Shell

## ID: test-single-workflow-8
## Date: 2026-01-29
## Status: Experiment Defined
## Trigger: Founder input in `product/feedback/inbox.md`

## Overview

This decision defines an experiment to establish the foundational React application shell, including a `shadcn/ui`-based design system, Google login, and a basic dashboard. This is crucial for enabling future user interaction and feature development.

## Hypothesis

As a technical founder/developer,
I believe implementing a `shadcn/ui`-based React app with Google login and a basic dashboard
will result in a rapid, consistent, and extensible foundation for future feature development
because it provides a modern design system and essential app shell components out-of-the-box, enabling faster iteration and a more intuitive user experience.

## Context

- **Affected Beliefs**:
    - "The primary user is technically competent" (Reinforced: building a modern dev-friendly stack)
    - "The product must feel obvious without documentation" (Supported: consistent UI aids intuition)
    - "Users value speed over configurability" (Supported: `shadcn/ui` offers speed and consistency)
- **Current Workflow**: No existing application shell; manual setup for each new feature.
- **Pain Point**: Lack of a unified, modern, and extensible front-end foundation slows down development and risks UI inconsistency.
- **Success Metric**:
    - Successful Google login rate for test users: 100%.
    - Time to integrate first new feature using the design system: < 1 day (internal developer metric).
    - Consistency of UI components: High subjective consistency.
- **Reversibility**: While core tech stack changes are significant, the minimal implementation allows for re-evaluation of `shadcn/ui` or authentication provider with manageable refactor if initial assumptions are invalid. The architectural choice itself is the 'experiment.'

## Experiment Scope

- **Size**: `size: medium` (4-7 days)
- **Component**: `frontend`
- **Phase**: `phase-1-mvp`
- **Description**:
    - Initialize a React application.
    - Integrate `shadcn/ui` as the primary design system.
    - Implement a Google OAuth login flow.
    - Create a basic dashboard page with mock content accessible post-login.
    - Establish clear guidelines for using `shadcn/ui` components within the project.

## Success Evaluation

- **Metric**:
    - Google login success rate.
    - Developer feedback on ease of use of the design system.
    - Visual consistency of implemented components.
- **Target**:
    - 100% successful Google login for internal testers.
    - Positive developer feedback on design system integration speed.
    - Visually consistent UI across login and dashboard.
- **Measured via**: Internal testing, developer feedback, visual inspection.
- **Timeline**: Evaluate after 1 week post-initial deployment.
- **If successful**: The current beliefs are reinforced. The established design system and app shell become the foundation for subsequent features. Document learnings.
- **If unsuccessful**: Re-evaluate the choice of `shadcn/ui`, React, or Google authentication. Document specific challenges and update beliefs/strategy accordingly.

## Next Steps

- Create GitHub issue for implementation.
- Handoff to Design Agent for initial UI/UX considerations if needed beyond `shadcn/ui` defaults.
