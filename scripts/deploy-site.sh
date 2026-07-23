#!/usr/bin/env bash
# Deploy one SSG storefront to Cloudflare Pages (static assets only).
# Usage: ./scripts/deploy-site.sh <slug>
# Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SLUG="${1:-}"
if [[ -z "$SLUG" || ! -d "sites/$SLUG" ]]; then
  echo "Usage: $0 <slug>"
  echo "Sites: $(ls -1 sites | tr '\n' ' ')"
  exit 1
fi

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" || -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]]; then
  echo "Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID"
  exit 1
fi

PKG=$(node -p "require('./sites/${SLUG}/package.json').name")
PROJECT="ecom-dropship-${SLUG}"
OUT="sites/${SLUG}/.output/public"

echo "==> Build ${PKG}"
pnpm --filter "$PKG" build

if [[ ! -f "${OUT}/index.html" ]]; then
  echo "Missing ${OUT}/index.html — SSG build failed"
  exit 1
fi

echo "==> Deploy ${PROJECT} from ${OUT}"
pnpm exec wrangler pages deploy "$OUT" \
  --project-name="$PROJECT" \
  --commit-dirty=true

echo "Done. https://${PROJECT}.pages.dev"
