# Dev Environment Service

A standalone development service that implements features based on design/architecture specifications.

## Architecture

```
Pipeline → Webhook → Dev Service → Iterative Development → Commit → Callback
```

## Features

- ✅ Dedicated persistent environment for development
- ✅ Iterative build/fix loop (no workflow reruns needed)
- ✅ Automatic dependency detection and installation
- ✅ Multi-language support (Node.js, Python, Go, Rust, etc.)
- ✅ Integrates with GitHub via GitHub App
- ✅ Status updates via GitHub Status API
- ✅ Error context preservation between attempts

## Components

### 1. GitHub App Configuration

- Name: `AID Dev Service`
- Webhook URL: `https://your-service.com/webhook` (optional - for future webhook integration)
- Permissions:
  - Contents: Read & Write
  - Pull Requests: Read & Write
  - Statuses: Read & Write
  - Metadata: Read
- Events:
  - No specific events required (pipeline calls service directly via HTTP)

**Note:** The dev service is called directly by the pipeline via HTTP POST, not through GitHub webhooks. The GitHub App is only used for authentication to read/write repository content.

### 2. Dev Service (`app.py`)

- Flask/FastAPI web service
- Receives webhooks from pipeline
- Manages development workspaces
- Executes iterative development loops
- Reports status back to GitHub

### 3. Dev Agent (`dev_agent.py`)

- Reads design/architecture artifacts
- Generates code using LLM
- Builds and tests iteratively
- Fixes errors automatically
- Commits when successful

### 4. Build Manager (`build_manager.py`)

- Detects project type (package.json, requirements.txt, etc.)
- Runs appropriate build commands
- Captures and analyzes errors
- Manages dependencies

## Setup

### 1. Create GitHub App

1. Go to GitHub Settings → Developer settings → GitHub Apps → New GitHub App
2. Configure:
   - **Name**: `AID Dev Service`
   - **Homepage URL**: `https://github.com/your-org/AID`
   - **Webhook URL**: `https://your-dev-service.com/webhook`
   - **Webhook secret**: Generate a secure token
   - **Permissions**: See above
   - **Subscribe to events**: `repository_dispatch`
3. Generate private key and download
4. Install app on your repository

### 2. Deploy Dev Service

```bash
# Install dependencies
cd dev-service
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GitHub App credentials

# Run service
python app.py
```

### 3. Update Pipeline

The pipeline's dev stage now calls the service directly:

```yaml
dev:
  runs-on: ubuntu-latest
  steps:
    - name: Trigger Dev Service
      run: |
        curl -X POST https://your-dev-service.com/dev-request \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer ${{ secrets.DEV_SERVICE_TOKEN }}" \
          -d '{
            "feature_id": "${{ inputs.feature_id }}",
            "branch": "feature/${{ inputs.feature_id }}",
            "repository": "${{ github.repository }}"
          }'
```

## Workflow

1. **Pipeline calls dev service** via HTTP POST to `/dev-request`
2. **Dev service receives request** with feature_id and branch
3. **Service clones/pulls feature branch** into workspace
4. **Reads design artifacts** from `.ai/pipeline/{feature_id}.*`
5. **Generates initial code** using dev agent + LLM
6. **Iterative development loop**:
   - Detect project type and build commands
   - Install dependencies
   - Run build
   - If build fails:
     - Extract error messages
     - Call LLM to analyze and fix
     - Apply fixes
     - Retry build
   - Run tests
   - If tests fail:
     - Extract failures
     - Call LLM to fix
     - Apply fixes
     - Retry tests
7. **Commits and pushes** when all passing
8. **Updates GitHub Status** to signal pipeline continuation
9. **Pipeline QA stage** validates the committed code

## Configuration

### Environment Variables

```bash
# GitHub App
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# Repository
GITHUB_REPO_OWNER=your-org
GITHUB_REPO_NAME=AID

# LLM
AI_PROVIDER=gemini
GOOGLE_API_KEY=your-api-key
MODEL=gemini-2.0-flash-exp

# Service
DEV_SERVICE_PORT=8080
WORKSPACE_DIR=/var/dev-workspaces
MAX_BUILD_ATTEMPTS=5
MAX_TEST_ATTEMPTS=3
```

## Advantages Over Workflow-Based Dev

| Feature            | Workflow                    | Dev Service              |
| ------------------ | --------------------------- | ------------------------ |
| Build retries      | Restart entire workflow     | Loop in same environment |
| Dependency caching | Lost between runs           | Persistent               |
| Development time   | 5-10 minutes + queue        | 2-3 minutes              |
| Cost               | Every retry = full workflow | Single environment       |
| Iteration speed    | Slow (queue + setup)        | Fast (already running)   |
| Multi-feature      | Sequential only             | Parallel capable         |
| Error context      | Lost on restart             | Preserved                |

## Security

- ✅ GitHub App authentication (more secure than PAT)
- ✅ Webhook signature verification
- ✅ Sandboxed workspaces per feature
- ✅ No secrets in logs
- ✅ Automatic cleanup of old workspaces

## Monitoring

The service exposes metrics at `/metrics`:

```
dev_builds_total{status="success|failure"}
dev_build_duration_seconds
dev_llm_calls_total
dev_active_workspaces
```

## Future Enhancements

- [ ] Web UI for monitoring active developments
- [ ] Manual intervention for stuck builds
- [ ] Multi-repo support
- [ ] Distributed workspaces (multiple machines)
- [ ] Integration with Copilot Workspace
