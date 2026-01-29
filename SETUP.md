# AID Pipeline Setup

## Prerequisites

1. **Python 3.11+**
2. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
3. **GitHub CLI** (optional) - For workflow execution

## Python Installation

### Windows

**Option 1: Install from Python.org (Recommended)**

```powershell
# Download and install from:
# https://www.python.org/downloads/

# IMPORTANT: Check "Add Python to PATH" during installation
```

**Option 2: Install via Winget**

```powershell
winget install Python.Python.3.11
```

**Option 3: Install via Chocolatey**

```powershell
choco install python --version=3.11
```

**Verify Installation:**

```powershell
python --version
# or
python3 --version
# Should show: Python 3.11.x or higher
```

### macOS

```bash
# Using Homebrew
brew install python@3.11

# Verify
python3 --version
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip

# Fedora
sudo dnf install python3.11

# Verify
python3 --version
```

## Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd AID
```

### 2. Install Python Dependencies

**Windows (PowerShell):**

```powershell
# Try python first
python -m pip install -r requirements.txt

# If that doesn't work, try python3
python3 -m pip install -r requirements.txt

# Or use pip directly
pip install -r requirements.txt
```

**macOS/Linux:**

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

### 3. Configure API Key

**Local Development:**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace sk-your-api-key-here with your actual key
nano .env  # or use any text editor
```

Your `.env` file should look like:

```
OPENAI_API_KEY=sk-proj-abc123...
```

**GitHub Actions:**

1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key
5. Click "Add secret"

## Testing Locally

### Test Product Agent

**Windows (PowerShell):**

```powershell
# Direct invocation (recommended for Windows)
python scripts/invoke_product_agent.py test-feature "Testing the setup"
# or
py scripts/invoke_product_agent.py test-feature "Testing the setup"

# Git Bash (if installed)
bash scripts/test_product_agent.sh
```

**macOS/Linux:**

```bash
# Run the test script
bash scripts/test_product_agent.sh

# Or invoke directly
python3 scripts/invoke_product_agent.py test-feature "Testing the setup"
```

This will:

- ✅ Verify OPENAI_API_KEY is set
- ✅ Check Python and dependencies
- ✅ Invoke Product Agent with GPT-4.1
- ✅ Generate decision record, experiment, and issue

### Expected Outputs

After successful test:

- `product/decisions/<date>-test-feature.md` - Decision record
- `experiments/active.md` - Updated with new experiment
- `.ai/pipeline/test-feature-issue.md` - GitHub issue content

## Running the Pipeline

### Via GitHub Actions (Recommended)

```bash
# Trigger the pipeline
gh workflow run pipeline.yml \
  -f feature_id=onboarding-v2 \
  -f stage=intake

# Check workflow status
gh run list --workflow=pipeline.yml

# View workflow logs
gh run view --log
```

### Locally (For Testing)

**Windows:**

```powershell
# 1. Product stage
python scripts/invoke_product_agent.py onboarding-v2
# or use: py scripts/invoke_product_agent.py onboarding-v2

# 2. Design stage (coming soon)
# python scripts/invoke_design_agent.py onboarding-v2

# 3. Dev stage (coming soon)
# python scripts/invoke_dev_agent.py onboarding-v2
```

**macOS/Linux:**

```bash
# 1. Product stage
python3 scripts/invoke_product_agent.py onboarding-v2

# 2. Design stage (coming soon)
# python3 scripts/invoke_design_agent.py onboarding-v2

# 3. Dev stage (coming soon)
# python3 scripts/invoke_dev_agent.py onboarding-v2
```

## Pipeline Status Tracking

````bash
# View currPython was not found (Windows)

**Solution 1: Install Python**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or higher
3. Run installer
4. **IMPORTANT**: Check "Add Python to PATH" option
5. Restart terminal/PowerShell
6. Verify: `python --version`

**Solution 2: Fix PATH**
```powershell
# Add Python to PATH manually
# 1. Search "Environment Variables" in Windows
# 2. Edit "Path" under System Variables
# 3. Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311
# 4. Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts
# 5. Click OK and restart terminal
````

**Solution 3: Use py launcher (Windows)**

```powershell
# Windows has a 'py' launcher
py --version
py -m pip install -r requirements.txt
py scripts/invoke_product_agent.py test-feature
```

### Error: OPENAI_API_KEY not found

**Windows:**

```powershell
# Ensure .env file exists
copy .env.example .env

# Edit and add your key (use notepad or any editor)
notepad .env
```

**macOS/Linux:**

```bash
# Ensure .env file exists
cp .env.example .env

# Edit and add your key
nano .env
```

### Error: openai module not found

**Windows:**

```powershell
python -m pip install openai python-dotenv
```

**macOS/Linux:**

```bash
pip install openai python-dotenv
```

## Troubleshooting

### Error: OPENAI_API_KEY not found

```bash
# Ensure .env file exists
cp .env.example .env

# Edit and add your key
nano .env
```

### Error: openai module not found

```bash
pip install openai
```

### Error: Invalid API key

- Verify your API key at https://platform.openai.com/api-keys
- Ensure the key has sufficient credits
- Check if the key is properly exported

### GitHub Actions failing

1. Verify `OPENAI_API_KEY` or `GOOGLE_API_KEY` secret is set in repository settings
2. Check workflow logs: `gh run view --log`
3. Ensure `scripts/` directory is committed to repository

## Model Configuration

The Product Agent supports multiple AI providers:

### OpenAI (Default)

- **GPT-4.1** - Most capable
- **GPT-4o** - Faster, cheaper
- **GPT-4-turbo** - Balance of speed and capability

Edit `.env`:

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
MODEL=gpt-4.1
```

### Google Gemini (Alternative)

- **gemini-2.5-pro** - Advanced reasoning, 2M context
- **gemini-3-flash** - Fast and cheap (45x cheaper than GPT-4.1!)
- **gemini-3-pro** - Highest intelligence

Edit `.env`:

```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...
MODEL=gemini-2.5-pro
```

See **[GEMINI-SETUP.md](GEMINI-SETUP.md)** for detailed Gemini configuration.

## Cost Estimation

### OpenAI Pricing

GPT-4.1 (approximate):

- **Input**: $10 / 1M tokens
- **Output**: $30 / 1M tokens
- **Cost per run**: ~$0.09

### Google Gemini Pricing (Alternative)

Gemini 2.5 Pro:

- **Input**: $1.25 / 1M tokens
- **Output**: $10 / 1M tokens
- **Cost per run**: ~$0.056 (38% cheaper)

Gemini 3 Flash:

- **Input**: $0.10 / 1M tokens
- **Output**: $0.30 / 1M tokens
- **Cost per run**: ~$0.002 (98% cheaper!)

💡 **Tip**: Use Gemini 3 Flash for development, 2.5 Pro for production.

## Model Configuration

The Product Agent uses **GPT-4.1** by default.

To change the model, edit `scripts/invoke_product_agent.py`:

```python
MODEL = "gpt-4.1"  # Change to gpt-4o, gpt-4-turbo, etc.
```

## Cost Estimation

GPT-4.1 pricing (approximate):

- **Input**: $10 / 1M tokens
- **Output**: $30 / 1M tokens

Typical Product Agent execution:

- Input: ~3,000 tokens (agent instructions + context)
- Output: ~2,000 tokens (decision record + experiment + issue)
- **Cost per run**: ~$0.09

## Next Steps

1. ✅ Test Product Agent locally
2. ✅ Set up GitHub Actions secret
3. ✅ Run first pipeline workflow
4. 🔄 Implement Design Agent script
5. 🔄 Implement Dev Agent script
6. 🔄 Implement QA Agent script
7. 🔄 Implement Ops Agent script

## Documentation

- [Pipeline Architecture](.ai/PIPELINE.md)
- [Product Agent Details](.ai/agents/product.md)
- [Example Walkthrough](.ai/EXAMPLE-WALKTHROUGH.md)
- [Quick Reference](.ai/QUICK-REFERENCE.md)
