# Dev Service Setup Guide

## Prerequisites

1. **GitHub App**: You need to create a GitHub App with the following configuration
2. **Server**: A publicly accessible server to run the dev service
3. **API Keys**: Google API key (for Gemini) or OpenAI API key

## Step 1: Create GitHub App

1. Go to **GitHub Settings** → **Developer settings** → **GitHub Apps** → **New GitHub App**

2. Fill in the details:

   ```
   GitHub App name: AID Dev Service
   Homepage URL: https://github.com/ollehbom/AID
   Webhook URL: https://your-server.com/webhook
   Webhook secret: [Generate a random secret]
   ```

3. Set **Permissions**:
   - Repository permissions:
     - Contents: Read & Write
     - Pull requests: Read & Write
     - Statuses: Read & Write
     - Metadata: Read
   - Subscribe to events:
     - repository_dispatch

4. Click **Create GitHub App**

5. **Generate private key**:
   - After creation, scroll down to "Private keys"
   - Click "Generate a private key"
   - Save the downloaded `.pem` file

6. **Install the app**:
   - Go to "Install App" tab
   - Click "Install" next to your repository
   - Select "Only select repositories" → Choose "AID"
   - Click "Install"

## Step 2: Deploy Dev Service

### Option A: Docker (Recommended)

```bash
cd dev-service

# Copy environment file
cp .env.example .env

# Edit .env with your values
nano .env

# Copy your GitHub App private key
cp ~/Downloads/your-app.private-key.pem ./private-key.pem

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Option B: Direct Python

```bash
cd dev-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env
nano .env

# Copy private key
cp ~/Downloads/your-app.private-key.pem ./private-key.pem

# Run service
python app.py
```

### Option C: Production (with gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn --bind 0.0.0.0:8080 --workers 4 --timeout 600 app:app
```

## Step 3: Configure Tunnel (for local development)

If running locally, use ngrok or similar to expose your service:

```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Start tunnel
ngrok http 8080

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update your GitHub App webhook URL to: https://abc123.ngrok.io/webhook
```

## Step 4: Update Pipeline Workflow

The pipeline's dev stage should trigger the service instead of running directly.

Update `.github/workflows/pipeline.yml`:

```yaml
dev:
  needs: architect
  runs-on: ubuntu-latest
  permissions:
    contents: write
  steps:
    - uses: actions/checkout@v4
      with:
        ref: feature/${{ inputs.feature_id }}

    - name: Trigger Dev Service
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        echo "🚀 Triggering Dev Service for feature: ${{ inputs.feature_id }}"

        gh api repos/${{ github.repository }}/dispatches \
          -f event_type=dev_stage_ready \
          -f client_payload[feature_id]=${{ inputs.feature_id }} \
          -f client_payload[branch]=feature/${{ inputs.feature_id }}

        echo "✅ Dev Service triggered - development will happen asynchronously"
        echo "Monitor progress at: https://your-dev-service.com/status/${{ inputs.feature_id }}"

    - name: Wait for Dev Service completion
      run: |
        echo "⏳ Waiting for dev service to complete..."

        MAX_WAIT=1800  # 30 minutes
        ELAPSED=0

        while [ $ELAPSED -lt $MAX_WAIT ]; do
          # Check commit status on feature branch
          STATUS=$(gh api repos/${{ github.repository }}/commits/feature/${{ inputs.feature_id }}/status \
            --jq '.statuses[] | select(.context == "dev-service/build") | .state' \
            | head -1)
          
          if [ "$STATUS" = "success" ]; then
            echo "✅ Dev service completed successfully!"
            exit 0
          elif [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
            echo "❌ Dev service failed"
            exit 1
          fi
          
          echo "Status: ${STATUS:-pending} (${ELAPSED}s / ${MAX_WAIT}s)"
          sleep 30
          ELAPSED=$((ELAPSED + 30))
        done

        echo "⏰ Timeout waiting for dev service"
        exit 1

    - name: Pull latest changes from dev service
      run: |
        git pull origin feature/${{ inputs.feature_id }}

    - name: Update pipeline state
      run: |
        sed -i 's/status:.*/status: dev_complete/' .ai/pipeline/${{ inputs.feature_id }}.state
        sed -i 's/dev: .*/dev: ✓/' .ai/pipeline/${{ inputs.feature_id }}.state

        git config user.name "Pipeline Bot"
        git config user.email "pipeline@aid.local"
        git add .ai/pipeline/
        git commit -m "Dev: ${{ inputs.feature_id }} stage complete" || echo "No changes"
        git push
```

## Step 5: Test the Integration

1. **Check service health**:

   ```bash
   curl https://your-service.com/health
   ```

2. **Trigger a test development**:

   ```bash
   gh workflow run pipeline.yml -f feature_id=test-feature
   ```

3. **Monitor the dev service**:

   ```bash
   # View logs
   docker-compose logs -f dev-service

   # Check status
   curl https://your-service.com/status/test-feature
   ```

## Troubleshooting

### Webhook not receiving events

1. Check GitHub App webhook settings
2. Verify webhook URL is correct and accessible
3. Check webhook secret matches `.env`
4. Look at webhook delivery logs in GitHub App settings

### Dev service can't clone repository

1. Verify GitHub App has Contents: Read & Write permission
2. Check that the app is installed on the repository
3. Verify the installation ID is correct

### Build failures

1. Check dev service logs: `docker-compose logs -f`
2. Inspect workspace: `ls -la /var/dev-workspaces/feature-id/`
3. Manually test build commands in the workspace

### Status not updating

1. Verify GitHub App has Statuses: Read & Write permission
2. Check that feature branch exists
3. Look for errors in dev service logs

## Monitoring

The dev service exposes these endpoints:

- `GET /health` - Service health check
- `GET /status/<feature_id>` - Feature development status
- `POST /webhook` - GitHub webhook receiver

## Security

- ✅ Webhook signature verification
- ✅ GitHub App authentication (not PAT)
- ✅ Sandboxed workspaces per feature
- ✅ Private key not in logs
- ✅ Automatic workspace cleanup

## Next Steps

Once the basic setup is working, consider:

1. **Add monitoring** (Prometheus metrics at `/metrics`)
2. **Add web UI** for monitoring active developments
3. **Scale horizontally** (multiple dev service instances)
4. **Add Redis** for job queue (replace threading with Celery)
5. **Add manual intervention** API for stuck builds
