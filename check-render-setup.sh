#!/bin/bash
# Render Deployment Helper Script
# This script helps verify your setup before deploying to Render

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     DISHA Render Deployment Pre-Check                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check for Docker files
echo "📋 Checking deployment files..."
echo ""

if [ -f "Dockerfile" ]; then
    echo "❌ Dockerfile found (should be removed)"
    exit 1
else
    echo "✅ Dockerfile removed"
fi

if [ -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml found (should be removed)"
    exit 1
else
    echo "✅ docker-compose.yml removed"
fi

# Check for required files
required_files=("Procfile" "render.yaml" "runtime.txt" "wsgi.py" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "📝 Checking configurations..."
echo ""

# Check Procfile
if grep -q "gunicorn" Procfile; then
    echo "✅ Procfile has gunicorn configuration"
else
    echo "❌ Procfile missing gunicorn"
    exit 1
fi

# Check runtime.txt
if grep -q "python-3.11" runtime.txt; then
    echo "✅ runtime.txt specifies Python 3.11"
else
    echo "❌ runtime.txt Python version incorrect"
fi

# Check requirements.txt
if [ -s requirements.txt ]; then
    echo "✅ requirements.txt is populated"
    echo "   $(wc -l < requirements.txt) packages"
else
    echo "❌ requirements.txt is empty"
    exit 1
fi

# Check .env
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "MONGODB_URI" .env; then
        echo "  ✓ MONGODB_URI is configured"
    else
        echo "  ⚠ MONGODB_URI not found in .env"
    fi
else
    echo "⚠ .env file not found (you'll add it on Render)"
fi

# Check .gitignore
if grep -q ".env" .gitignore 2>/dev/null; then
    echo "✅ .env is in .gitignore (secrets safe)"
else
    echo "⚠ .env not in .gitignore (check if exposed)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Next steps:"
echo "  1. Read: RENDER_DEPLOYMENT_READY.md"
echo "  2. Go to: https://dashboard.render.com"
echo "  3. Create new Web Service from your GitHub repo"
echo "  4. Add environment variables (MONGODB_URI, SECRET_KEY, etc.)"
echo "  5. Deploy!"
echo ""
echo "📚 For detailed instructions, see:"
echo "  - RENDER_DEPLOYMENT_READY.md (Quick start)"
echo "  - RENDER_DEPLOYMENT.md (Detailed guide)"
echo "  - DEPLOYMENT_CHECKLIST.md (Step-by-step)"
echo ""
