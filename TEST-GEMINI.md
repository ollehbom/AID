# Test Gemini Integration

Test file to verify Gemini 2.5 Pro works with the Product Agent.

## Quick Test

```bash
# 1. Setup .env for Gemini
cp .env.example .env

# 2. Edit .env:
AI_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
MODEL=gemini-2.5-pro

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run test
python scripts/invoke_product_agent.py gemini-test
```

## Expected Output

```
🤖 Invoking Product Agent for feature: gemini-test
📅 Date: 2026-01-29
🤖 Provider: GEMINI
🤖 Model: gemini-2.5-pro

✅ Created decision record: product/decisions/2026-01-29-gemini-test.md
✅ Updated experiments: experiments/active.md
✅ Created GitHub issue content: .ai/pipeline/gemini-test-issue.md

📋 Summary:
[Gemini's analysis...]

✅ Product Agent execution complete!
👉 Next: Design Agent will process this in the next pipeline stage
```

## Model Comparison

Run the same test with different models:

### GPT-4.1 (OpenAI)

```bash
AI_PROVIDER=openai
MODEL=gpt-4.1
python scripts/invoke_product_agent.py openai-test
```

### Gemini 2.5 Pro

```bash
AI_PROVIDER=gemini
MODEL=gemini-2.5-pro
python scripts/invoke_product_agent.py gemini-test
```

### Gemini 3 Flash (Cheapest)

```bash
AI_PROVIDER=gemini
MODEL=gemini-3-flash
python scripts/invoke_product_agent.py gemini-flash-test
```

Compare the outputs!

## Troubleshooting

### Error: models/gpt-4.1 is not found

You need to change the MODEL in your .env file:

```bash
# Wrong - using OpenAI model name with Gemini provider
AI_PROVIDER=gemini
MODEL=gpt-4.1  # ❌ This won't work!

# Correct - use Gemini model name
AI_PROVIDER=gemini
MODEL=gemini-2.5-pro  # ✅ Correct
```

### Import Error: No module named 'google.genai'

```bash
pip install google-genai
```

**Note**: Use the NEW `google-genai` package (not the deprecated `google-generativeai`).

### GOOGLE_API_KEY not found

Check your .env file:

```bash
cat .env | grep GOOGLE_API_KEY
cat .env | grep AI_PROVIDER
```

### Invalid API key

1. Get new key: https://aistudio.google.com/apikey
2. Verify format starts with `AIzaSy`
3. No quotes needed in .env

### Model not found

Use stable model names:

- `gemini-2.5-pro` ✅
- `gemini-3-flash` ✅
- `gemini-pro` ❌ (old)
