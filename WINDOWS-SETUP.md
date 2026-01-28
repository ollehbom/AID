# Windows Quick Start Guide

## Step-by-Step Setup for Windows

### 1. Install Python

**Check if Python is already installed:**

```powershell
python --version
```

If you get "Python was not found", install it:

**Option A: From Python.org (Easiest)**

1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.11.x"
3. Run the installer
4. ✅ **CHECK "Add Python to PATH"** (CRITICAL!)
5. Click "Install Now"
6. Restart PowerShell/Terminal

**Option B: Using Winget**

```powershell
winget install Python.Python.3.11
```

**Verify Installation:**

```powershell
python --version
# Should show: Python 3.11.x
```

### 2. Install Dependencies

```powershell
# Navigate to project directory
cd C:\Dev\Training\AID

# Install packages
python -m pip install -r requirements.txt
```

### 3. Setup API Key

```powershell
# Copy example file
copy .env.example .env

# Edit with Notepad
notepad .env

# Add your OpenAI API key (replace the placeholder):
# OPENAI_API_KEY=sk-proj-your-actual-key-here

# Save and close Notepad
```

### 4. Test It Works

```powershell
# Add some test feedback
echo "### 2026-01-28 (Founder)" >> product/feedback/inbox.md
echo "- Test feedback for setup" >> product/feedback/inbox.md

# Run Product Agent
python scripts/invoke_product_agent.py test-setup
```

Expected output:

```
🤖 Invoking Product Agent for feature: test-setup
📅 Date: 2026-01-28
🤖 Model: gpt-4.1

✅ Created decision record: product/decisions/2026-01-28-test-setup.md
✅ Updated experiments: experiments/active.md
✅ Created GitHub issue content: .ai/pipeline/test-setup-issue.md

📋 Summary:
[Agent's analysis summary]

✅ Product Agent execution complete!
```

## Common Windows Issues

### Issue 1: "python is not recognized"

**Solution A: Use py launcher**

```powershell
py --version
py -m pip install -r requirements.txt
py scripts/invoke_product_agent.py test-feature
```

**Solution B: Add Python to PATH**

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "System variables", find "Path", click "Edit"
4. Click "New" and add:
   ```
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python311
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts
   ```
5. Click OK on all windows
6. Restart PowerShell
7. Test: `python --version`

### Issue 2: "pip is not recognized"

```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt

# or with py launcher
py -m pip install -r requirements.txt
```

### Issue 3: Permission denied errors

```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → Run as Administrator

# Or install for user only
python -m pip install --user -r requirements.txt
```

### Issue 4: Can't run bash scripts

**Option A: Install Git Bash**

1. Install Git for Windows: https://git-scm.com/download/win
2. Use Git Bash terminal
3. Run: `bash scripts/test_product_agent.sh`

**Option B: Use Python directly (Recommended)**

```powershell
# Skip bash scripts, use Python directly
python scripts/invoke_product_agent.py test-feature
```

### Issue 5: .env file not loading

```powershell
# Verify file exists
dir .env

# Check content (should have your API key)
type .env

# Re-copy from example if needed
copy .env.example .env
notepad .env
```

## PowerShell vs Command Prompt vs Git Bash

**PowerShell (Recommended):**

- Built into Windows
- Modern, powerful
- Use: `python`, `copy`, `dir`

**Command Prompt:**

- Legacy Windows terminal
- Use: `python`, `copy`, `dir`

**Git Bash:**

- Linux-like environment
- Use: `python3`, `cp`, `ls`, `bash scripts/`

Choose whichever you're comfortable with!

## Quick Reference

| Task         | PowerShell Command                                    |
| ------------ | ----------------------------------------------------- |
| Check Python | `python --version`                                    |
| Install deps | `python -m pip install -r requirements.txt`           |
| Copy .env    | `copy .env.example .env`                              |
| Edit .env    | `notepad .env`                                        |
| Run agent    | `python scripts/invoke_product_agent.py feature-name` |
| View files   | `dir` or `ls`                                         |
| Change dir   | `cd C:\path\to\dir`                                   |

## VS Code Integration (Optional)

If you use VS Code:

1. Install Python extension
2. Open Command Palette (`Ctrl+Shift+P`)
3. Type "Python: Select Interpreter"
4. Choose Python 3.11

Now you can run scripts directly in VS Code terminal!

## Next Steps

Once setup is complete:

1. ✅ Python installed and in PATH
2. ✅ Dependencies installed
3. ✅ .env file created with API key
4. ✅ Test run successful

**Continue to:**

- [SETUP.md](SETUP.md) - Full documentation
- [PRODUCT-AGENT-QUICKSTART.md](PRODUCT-AGENT-QUICKSTART.md) - Quick start guide
- [.env.README.md](.env.README.md) - Environment configuration
