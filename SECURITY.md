# Security Best Practices

## Environment Variables

### ✅ Using .env File (Recommended)

**Why:**

- API keys are never committed to git
- Easy to manage across different environments
- No risk of accidentally exposing keys in code or documentation

**Setup:**

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Add your actual key
# Edit .env and replace sk-your-api-key-here with your real key

# 3. Verify it's in .gitignore
cat .gitignore | grep .env
```

**What's Protected:**

- `.env` is in `.gitignore` - Never committed
- `.env.example` is committed - No sensitive data, just template
- GitHub Actions uses repository secrets - Encrypted at rest

### ❌ Don't Do This

```bash
# ❌ Don't export in shell (lost on restart)
export OPENAI_API_KEY="sk-..."

# ❌ Don't hardcode in scripts
api_key = "sk-..."

# ❌ Don't commit .env to git
git add .env  # This should be blocked by .gitignore
```

## Verifying Your Setup

```bash
# Check .env exists and has your key
cat .env | grep OPENAI_API_KEY

# Check .env is ignored by git
git status | grep .env
# Should NOT appear in untracked files

# Test it works
python scripts/invoke_product_agent.py test-feature
```

## Rotating API Keys

If your key is compromised:

1. **Revoke old key** at https://platform.openai.com/api-keys
2. **Generate new key**
3. **Update .env file**:
   ```bash
   nano .env  # Replace with new key
   ```
4. **Update GitHub secret** (if using Actions):
   - Settings → Secrets → Edit OPENAI_API_KEY

## Multi-Environment Setup

For different environments (dev, staging, prod):

```bash
# Development
.env              # Your local dev key

# Staging
.env.staging      # Load with: python-dotenv load_dotenv('.env.staging')

# Production
# Use GitHub Actions secrets or cloud provider secret management
```

## What Gets Committed

✅ **Safe to commit:**

- `.env.example` - Template without real keys
- `.gitignore` - Protects .env
- Documentation mentioning .env setup
- Scripts that read from .env

❌ **Never commit:**

- `.env` - Contains real API key
- Any file with hardcoded keys
- Screenshots showing API keys
- Log files with keys

## Additional Security

1. **Limit API key permissions** (if supported by provider)
2. **Set spending limits** on your OpenAI account
3. **Regularly rotate keys** (every 90 days)
4. **Use separate keys** for dev/prod
5. **Monitor API usage** for anomalies

## GitHub Actions Security

Your workflow uses `${{ secrets.OPENAI_API_KEY }}`:

- Stored encrypted at rest
- Masked in workflow logs
- Only accessible to workflow runs
- Can be rotated without code changes

**To update:**

1. Repository → Settings → Secrets and variables → Actions
2. Click OPENAI_API_KEY
3. Update value
4. Click "Update secret"

## Questions?

- Lost your .env? Copy from `.env.example` and re-add key
- Key not working? Verify at https://platform.openai.com/api-keys
- Accidentally committed .env? Use `git rm --cached .env` and rotate key
