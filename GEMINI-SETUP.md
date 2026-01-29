# Using Google Gemini with AID

## Quick Setup

### 1. Get API Key

Go to https://aistudio.google.com/apikey and create an API key.

### 2. Configure .env

```bash
# Copy example
cp .env.example .env

# Edit .env and set:
AI_PROVIDER=gemini
GOOGLE_API_KEY=your-actual-key-here
MODEL=gemini-2.5-pro
```

Your `.env` should look like:

```
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSyAbc123...
MODEL=gemini-2.5-pro
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
# Or install directly: pip install google-genai
```

**Note**: AID uses the new `google-genai` package (not the deprecated `google-generativeai`).

### 4. Test

```bash
python scripts/invoke_product_agent.py test-gemini
```

## Available Gemini Models

### Gemini 2.5 Pro (Recommended)

- **Model**: `gemini-2.5-pro`
- **Best for**: Complex reasoning, code analysis, long context
- **Context**: Up to 2M tokens
- **Cost**: $1.25/1M input tokens, $10/1M output tokens

### Gemini 3 Flash

- **Model**: `gemini-3-flash`
- **Best for**: Speed, balanced capabilities
- **Context**: Up to 1M tokens
- **Cost**: $0.10/1M input tokens, $0.30/1M output tokens

### Gemini 3 Pro

- **Model**: `gemini-3-pro`
- **Best for**: Highest intelligence, multimodal
- **Context**: Up to 2M tokens
- **Cost**: $2.50/1M input tokens, $10/1M output tokens

## Configuration Examples

### Use Gemini 2.5 Pro (default)

```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...
MODEL=gemini-2.5-pro
TEMPERATURE=0.7
```

### Use Gemini Flash (faster, cheaper)

```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...
MODEL=gemini-3-flash
TEMPERATURE=0.7
```

### Use Latest Version

```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...
MODEL=gemini-flash-latest  # Always latest flash model
TEMPERATURE=0.7
```

## Switching Between OpenAI and Gemini

Just change `AI_PROVIDER` in `.env`:

**For OpenAI:**

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
MODEL=gpt-4.1
```

**For Gemini:**

```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...
MODEL=gemini-2.5-pro
```

No code changes needed! The script automatically uses the right provider.

## Cost Comparison

### Product Agent Execution (~5,000 tokens total)

| Model          | Input Cost | Output Cost | Total      |
| -------------- | ---------- | ----------- | ---------- |
| GPT-4.1        | $0.03      | $0.06       | **$0.09**  |
| GPT-4o         | $0.015     | $0.03       | **$0.045** |
| Gemini 2.5 Pro | $0.006     | $0.05       | **$0.056** |
| Gemini 3 Flash | $0.0005    | $0.0015     | **$0.002** |

**Gemini 3 Flash is 45x cheaper than GPT-4.1!**

## Features

### ✅ Supported

- Text generation with JSON output
- Long context (up to 2M tokens with 2.5 Pro)
- Structured outputs
- Temperature control
- Reasoning and code analysis

### ⚠️ Differences from OpenAI

- System prompts are combined with user prompts
- Higher token limits (2M vs 128K for GPT-4)
- Different pricing model
- Faster inference (Flash models)

## Troubleshooting

### Error: No module named 'google.genai'

```bash
pip install google-genai
```

**Important**: Use `google-genai` (new), not `google-generativeai` (deprecated).

### Error: GOOGLE_API_KEY not found

```bash
# Check .env file
cat .env | grep GOOGLE_API_KEY

# Ensure AI_PROVIDER is set
cat .env | grep AI_PROVIDER
```

### Error: Invalid API key

1. Verify key at https://aistudio.google.com/apikey
2. Ensure no extra spaces in .env
3. Check key format starts with `AIzaSy`

### Error: Model not found

```bash
# Use stable model names:
MODEL=gemini-2.5-pro      # ✅ Correct
MODEL=gemini-2.5-flash    # ✅ Correct
MODEL=gemini-pro          # ❌ Old format
```

### Rate Limit Exceeded

Gemini has generous free tier limits:

- 2.5 Pro: 1,500 requests/day (free)
- 3 Flash: 10,000 requests/day (free)

For higher limits, enable billing in Google AI Studio.

## GitHub Actions

Update workflow secret:

1. Repository Settings → Secrets → Actions
2. Add `GOOGLE_API_KEY` with your key
3. Update `.github/workflows/pipeline.yml`:

```yaml
env:
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  AI_PROVIDER: gemini
  MODEL: gemini-2.5-pro
```

## Benefits of Gemini

✅ **Lower cost** - Up to 45x cheaper than GPT-4  
✅ **Longer context** - 2M tokens vs 128K  
✅ **Fast inference** - Flash models are very quick  
✅ **Great reasoning** - 2.5 Pro excels at complex tasks  
✅ **Free tier** - Generous limits for development  
✅ **No vendor lock-in** - Easy to switch providers

## Recommended Setup

For development:

```bash
AI_PROVIDER=gemini
MODEL=gemini-3-flash
GOOGLE_API_KEY=...
```

For production:

```bash
AI_PROVIDER=gemini
MODEL=gemini-2.5-pro
GOOGLE_API_KEY=...
```

## Documentation

- Google AI Studio: https://aistudio.google.com
- API Docs: https://ai.google.dev/gemini-api/docs
- Model Info: https://ai.google.dev/gemini-api/docs/models
- Pricing: https://ai.google.dev/gemini-api/docs/pricing
