#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"

echo "→ Deploying to Cloudflare Pages..."
wrangler pages deploy . --project-name whynotx --branch main --commit-dirty=true 2>&1 | tail -3
echo "  Live at: https://whynotx.pages.dev/"
