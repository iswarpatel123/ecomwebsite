#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <slug>"
  echo "Example: $0 katachi"
  exit 1
fi

SLUG="$1"
CLONE_PATH=".cloning/${SLUG}"
SITE_PATH="sites/${SLUG}"

# Validate slug
if ! [[ "$SLUG" =~ ^[a-z0-9-]+$ ]]; then
  echo "Error: Slug must contain only lowercase letters, numbers, and hyphens"
  exit 1
fi

# Check if clone workspace already exists
if [ -d "$CLONE_PATH" ]; then
  echo "Error: Clone workspace already exists: $CLONE_PATH"
  exit 1
fi

# Check if site directory already exists
if [ -d "$SITE_PATH" ]; then
  echo "Error: Site directory already exists: $SITE_PATH"
  exit 1
fi

echo "Initializing site: $SLUG"

# Step 1: Create clone workspace
echo "Step 1: Creating clone workspace..."
cp -r .cloning/_template "$CLONE_PATH"
echo "✓ Created clone workspace: $CLONE_PATH"

# Step 2: Copy template as blank site
echo "Step 2: Copying template as blank site..."
cp -r sites/template "$SITE_PATH"
echo "✓ Copied template to $SITE_PATH"

# Step 3: Update package.json
echo "Step 3: Updating package.json..."

# Calculate port (3000 + number of existing sites % 100)
PORT=$((3000 + $(ls -d sites/*/ 2>/dev/null | wc -l) % 100))
PORT_PREVIEW=$((PORT + 100))

sed -i "s/@dropshipping\/template-site/@dropshipping\/site-${SLUG}/g" "$SITE_PATH/package.json"
sed -i "s/3000/${PORT}/g" "$SITE_PATH/package.json"
sed -i "s/3100/${PORT_PREVIEW}/g" "$SITE_PATH/package.json"
sed -i "s/3000/${PORT}/g" "$SITE_PATH/playwright.config.ts"
echo "✓ Updated package.json (port: ${PORT})"
sed -i "s/3100/${PORT_PREVIEW}/g" "$SITE_PATH/playwright.config.ts"

# Step 4: Install dependencies
echo "Step 4: Installing dependencies..."
cd "$SITE_PATH"
pnpm install
echo "✓ Dependencies installed"

echo ""
echo "✅ Site '$SLUG' initialized successfully!"
echo ""
echo "Next steps:"
echo "  cd $SITE_PATH"
echo "  npm run dev"
