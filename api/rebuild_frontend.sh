#!/bin/bash
# 本地重建前端静态资源并部署到 Django（macOS 原生，无 Docker）
# 解决 nuxt generate 输出 .output/public 与 Django 期望目录层级不一致的问题
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/packages/frontend/.output/public"
DST="$REPO/api/src/frontend"

cd "$REPO/packages"
npm run --workspace=frontend generate

# 静态资源（_nuxt/excalidraw/favicon 等）→ api/src/frontend/static/（直接层）
rm -rf "$DST/static"
mkdir -p "$DST/static"
cp -R "$OUT/static/." "$DST/static/"

# SPA 路由目录（可选，catch-all 会兜底，但保持一致）
for d in 200.html 404.html backups designs license login notes plugins projects settings shared templates users; do
  [ -e "$OUT/$d" ] && cp -R "$OUT/$d" "$DST/static/"
done

# 首页 → api/src/frontend/index.html
cp "$OUT/index.html" "$DST/index.html"

# 校验 entry 与资源对齐
entry="$(grep -o '/static/_nuxt/[^"]*\.js' "$DST/index.html" | head -1)"
[ -f "$DST/static${entry#/static}" ] && echo "✓ frontend rebuilt, entry ok: $entry" || { echo "✗ entry missing: $entry"; exit 1; }
