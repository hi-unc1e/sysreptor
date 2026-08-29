#!/bin/bash
# 本地原生启动 SysReptor（macOS，无 Docker）
# 依赖：brew services 的 postgresql@14 + redis；前端已 generate 到 api/src/frontend/static
set -e
cd "$(dirname "$0")"

export SECRET_KEY="${SECRET_KEY:-localdev-only-not-secret}"
export DEBUG=off
export ALLOWED_HOSTS=localhost,127.0.0.1
export DATABASE_NAME=sysreptor
export DATABASE_USER="${DATABASE_USER:-$(whoami)}"
export DATABASE_HOST=localhost
export DATABASE_PASSWORD=
export REDIS_URL=redis://localhost:6379/0
export CELERY_TASK_ALWAYS_EAGR=1
export CELERY_TASK_ALWAYS_EAGER=1
export PREFERRED_LANGUAGES=zh-CN,en-US
export CHROMIUM_EXECUTABLE="${CHROMIUM_EXECUTABLE:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
export PDF_RENDER_SCRIPT_PATH="$(cd .. && pwd)/packages/rendering/dist/bundle.js"

exec .venv/bin/uvicorn --app-dir src sysreptor.conf.asgi:application --host 127.0.0.1 --port "${PORT:-8001}"
