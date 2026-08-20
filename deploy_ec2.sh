#!/bin/bash
# =================================================================
# Workforce OS - AWS EC2 One-Click Redeployment Script
# =================================================================

set -e

TAG=$1

echo "🚀 Starting Workforce OS Redeployment on EC2..."

# 1. Fetch Latest Code & Git Tags from dev Branch
echo "📥 Fetching tags and updates from dev branch..."
git fetch --tags origin

if [ -n "$TAG" ]; then
    echo "🏷️  Checking out release tag: $TAG..."
    git checkout "$TAG"
else
    echo "🌿 Checking out latest code from 'dev' branch..."
    git checkout dev || git checkout -b dev origin/dev
    git pull origin dev
fi

# 2. Update & Restart Backend Service
echo "🐍 Updating Backend Python Environment..."
cd backend
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "⚠️  backend/.env not found, copying from .env.example..."
    cp .env.example .env
fi

echo "🔄 Seeding / Initializing DB schema..."
python -m app.db.init_db || true

echo "🔁 Restarting FastAPI Backend Service..."
UVICORN_BIN=""
if [ -f ".venv/bin/uvicorn" ]; then
    UVICORN_BIN=".venv/bin/uvicorn"
elif [ -f "venv/bin/uvicorn" ]; then
    UVICORN_BIN="venv/bin/uvicorn"
else
    UVICORN_BIN="$(which uvicorn || echo 'uvicorn')"
fi

echo "Using uvicorn binary: $UVICORN_BIN"

if systemctl is-active --quiet employee-backend; then
    sudo systemctl restart employee-backend
elif command -v pm2 &> /dev/null; then
    pm2 delete employee-backend 2>/dev/null || true
    pm2 start "$UVICORN_BIN" --name "employee-backend" --cwd "$(pwd)" --interpreter none -- main:app --host 127.0.0.1 --port 8000 --workers 2
    pm2 save 2>/dev/null || true
else
    echo "⚠️  No systemd service or PM2 detected. Please ensure your backend process manager is running."
fi

# 3. Clean Disk Caches & Build Frontend Assets
echo "🧹 Cleaning previous web builds & package manager caches..."
cd ../web
rm -rf build node_modules/.vite
if command -v bun &> /dev/null; then
    bun pm cache rm || true
else
    npm cache clean --force || true
fi

echo "⚡ Building Fresh Frontend Assets..."
export NODE_OPTIONS="--max-old-space-size=1024"
if command -v bun &> /dev/null; then
    bun install
    bun run build
else
    npm install
    npm run build
fi

# 4. Clean Nginx Web Root & Copy Fresh Build
if [ -d "/var/www/html" ]; then
    echo "🧹 Removing previous build files from /var/www/html..."
    sudo rm -rf /var/www/html/*
    echo "🌐 Copying fresh production build files to /var/www/html..."
    sudo cp -r build/client/* /var/www/html/
fi

# 5. Reload Nginx
echo "🔄 Reloading Nginx Web Server..."
if command -v nginx &> /dev/null; then
    sudo systemctl reload nginx || sudo service nginx reload
fi

echo "✅ REDEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "Website is live at: https://vijeeth.zapto.org"
