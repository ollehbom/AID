#!/bin/bash
# Test script for Product Agent invocation

set -e

echo "🧪 Testing Product Agent Script"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo ""
    echo "Create one with:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your OPENAI_API_KEY"
    exit 1
fi

echo "✅ .env file found"

# Check if OPENAI_API_KEY is set in .env
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY may not be set properly in .env"
    echo "Make sure it starts with 'sk-' and is not the example value"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
if python3 -c "import openai" 2>/dev/null; then
    echo "✅ openai package installed"
else
    echo "❌ openai package not found"
    echo "Installing..."
    pip install openai
fi

# Run a test invocation
echo ""
echo "🤖 Running Product Agent test..."
echo ""

python3 scripts/invoke_product_agent.py test-feature "Test invocation to verify setup"

echo ""
echo "✅ Test complete!"
echo ""
echo "Check the following files were created:"
echo "  - product/decisions/<date>-test-feature.md"
echo "  - experiments/active.md (updated)"
echo "  - .ai/pipeline/test-feature-issue.md"
