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
# 1. Set up environment
cp .env.example .env
# Edit .env and add your API key
pip install -r requirements.txt

# 2. Test Product Agent locally
python scripts/invoke_product_agent.py test-feature

# 3. Start pipeline via GitHub Actions
gh workflow run pipeline.yml -f feature_id=my-feature -f stage=intake

# 4. Check pipeline status
cat .ai/pipeline/my-feature.state

# Continue to next stage
gh workflow run pipeline.yml -f feature_id=my-feature
```

---

## Quick Example

```bash
# 1. Add feedback to inbox
echo "### 2026-01-28 (Founder)
- Users confused by signup flow
- Too many steps before value" >> product/feedback/inbox.md

# 2. Invoke Product Agent
python scripts/invoke_product_agent.py signup-simplification

# 3. Agent analyzes and outputs:
#    ✅ product/decisions/2026-01-28-signup-simplification.md
#    ✅ experiments/active.md (updated)
#    ✅ .ai/pipeline/signup-simplification-issue.md
#    ✅ Creates GitHub issue

# 4. Review outputs
cat product/decisions/2026-01-28-signup-simplification.md

# 5. Continue pipeline (Design Agent next)
gh workflow run pipeline.yml -f feature_id=signup-simplification
```

---

## Documentation

- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[GEMINI-SETUP.md](GEMINI-SETUP.md)** - Using Google Gemini 2.5 Pro (cheaper alternative)
- **[WINDOWS-SETUP.md](WINDOWS-SETUP.md)** - Windows-specific quick start guide
- **[SECURITY.md](SECURITY.md)** - API key security and .env best practices
- **[PRODUCT-AGENT-QUICKSTART.md](PRODUCT-AGENT-QUICKSTART.md)** - 5-minute Product Agent guide
- [Pipeline Architecture](.ai/PIPELINE.md) - Stage definitions and handoff rules
- [Architecture Review](.ai/ARCHITECTURE-REVIEW.md) - Requirements verification
- [Orchestrator](.ai/workflows/pipeline-orchestrator.md) - Coordination logic
- [Agents](.ai/agents/) - Individual agent responsibilities
- [Example Walkthrough](.ai/EXAMPLE-WALKTHROUGH.md) - Complete feature lifecycle
- [Quick Reference](.ai/QUICK-REFERENCE.md) - Command cheat sheet

---

## Principles

- **Belief-driven**: Every change tests a hypothesis
- **Minimal scope**: Smallest reversible change
- **Sequential**: No skipping stages
- **Single-threaded**: One experiment at a time
