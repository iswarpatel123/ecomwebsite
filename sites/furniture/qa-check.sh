#!/bin/bash

# DOM/Functional QA for Furniture Hero Section
# Using curl and grep for simple DOM validation

echo "Starting DOM/Functional QA for Furniture Hero Section..."
echo "========================================================"
echo ""

# Check if server is running
echo "1. Checking dev server status..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001)
if [ "$HTTP_CODE" != "200" ]; then
    echo "✗ FAIL - Server not running (HTTP $HTTP_CODE)"
    exit 1
fi
echo "✓ PASS - Server running (HTTP 200)"
echo ""

# Check for h1 heading
echo "2. Checking for semantic heading (h1)..."
H1_COUNT=$(curl -s http://127.0.0.1:3001 | grep -c '<h1' || true)
if [ "$H1_COUNT" -gt 0 ]; then
    echo "✓ PASS - h1 heading found ($H1_COUNT instances)"
    TITLE=$(curl -s http://127.0.0.1:3001 | grep -o '<h1[^>]*>[^<]*</h1>' | head -1)
    if echo "$TITLE" | grep -qi "wanda sofa bed"; then
        echo "✓ PASS - h1 contains 'Wanda Sofa Bed'"
    else
        echo "✗ FAIL - h1 does not contain 'Wanda Sofa Bed'"
        echo "  Found: $TITLE"
    fi
else
    echo "✗ FAIL - No h1 heading found"
fi
echo ""

# Check for alt attributes on main image
echo "3. Checking image alt attributes..."
MAIN_ALT=$(curl -s http://127.0.0.1:3001 | sed -n '/<section[^>]*class="hero"[^>]*>/,/<\/section>/p' | grep -o 'alt="[^"]*"' | head -1)
if [ -n "$MAIN_ALT" ]; then
    echo "✓ PASS - Main image has alt attribute: $MAIN_ALT"
    if echo "$MAIN_ALT" | grep -qi "wanda sofa bed"; then
        echo "✓ PASS - Alt text contains 'Wanda Sofa Bed'"
    else
        echo "✗ FAIL - Alt text does not contain 'Wanda Sofa Bed'"
    fi
else
    echo "✗ FAIL - Main image missing alt attribute"
fi
echo ""

# Check for gallery controls (no 360 or gallery-view buttons)
echo "4. Checking for gallery controls (no 360/gallery-view)..."
if ! curl -s http://127.0.0.1:3001 | grep -qi 'data-360\|view-360\|view-gallery'; then
    echo "✓ PASS - No 360-view or gallery-view buttons found"
else
    echo "✗ FAIL - Found 360-view or gallery-view buttons"
fi

# Check for prev/next buttons
if curl -s http://127.0.0.1:3001 | grep -q 'hero__gallery-nav--previous\|hero__gallery-nav--next'; then
    echo "✓ PASS - Prev/Next buttons exist"
else
    echo "✗ FAIL - Prev/Next buttons not found"
fi

# Check for thumbnails
if curl -s http://127.0.0.1:3001 | grep -q 'hero__thumbnail'; then
    echo "✓ PASS - Thumbnail images exist"
else
    echo "✗ FAIL - Thumbnail images not found"
fi
echo ""

# Check for size selection (75/99)
echo "5. Checking size selection (75/99)..."
if curl -s http://127.0.0.1:3001 | grep -q 'hero__choice-button'; then
    echo "✓ PASS - Size options exist"
    SIZE_COUNT=$(curl -s http://127.0.0.1:3001 | sed -n '/<section[^>]*class="hero"[^>]*>/,/<\/section>/p' | grep -o 'hero__choice-button' | wc -l)
    if [ "$SIZE_COUNT" -gt 0 ]; then
        echo "✓ PASS - Size options found ($SIZE_COUNT buttons)"
    else
        echo "✗ FAIL - Size options not found"
    fi
else
    echo "✗ FAIL - Size options not found"
fi
echo ""

# Check for color selection
echo "6. Checking color selection..."
if curl -s http://127.0.0.1:3001 | grep -q 'hero__swatch\|hero__choice--colour'; then
    echo "✓ PASS - Color swatches exist"
else
    echo "✗ FAIL - Color swatches not found"
fi
echo ""

# Check for quantity input (now in ProductDescription component)
echo "7. Checking quantity controls..."
if curl -s http://127.0.0.1:3001 | grep -q 'pd__quantity\|aria-label="Quantity"'; then
    echo "✓ PASS - Quantity controls exist"
else
    echo "✗ FAIL - Quantity controls not found"
fi
echo ""

# Check min/max attributes (though it's using output with +/- buttons)
echo "8. Checking quantity buttons..."
if curl -s http://127.0.0.1:3001 | grep -q 'aria-label="Decrease quantity"\|aria-label="Increase quantity"'; then
    echo "✓ PASS - Quantity buttons have aria-labels"
else
    echo "✗ FAIL - Quantity buttons missing aria-labels"
fi
echo ""

# Check for add to cart button (now in ProductDescription component)
echo "9. Checking add to cart button..."
if curl -s http://127.0.0.1:3001 | grep -q 'pd__add-to-cart\|Add to cart'; then
    echo "✓ PASS - Add to cart button exists"
else
    echo "✗ FAIL - Add to cart button not found"
fi
echo ""

# Check for no remote https URLs in hero section
echo "10. Checking for no remote https URLs in hero..."
HERO_START=$(curl -s http://127.0.0.1:3001 | grep -o '<section[^>]*class="hero"[^>]*>' | wc -l)
if [ "$HERO_START" -gt 0 ]; then
    echo "✓ PASS - Hero section found"
    HTTPS_COUNT=$(curl -s http://127.0.0.1:3001 | sed -n '/<section[^>]*class="hero"[^>]*>/,/<\/section>/p' | grep -c 'https://' || true)
    if [ "$HTTPS_COUNT" -eq 0 ]; then
        echo "✓ PASS - No remote https URLs in hero section"
    else
        echo "✗ FAIL - Found $HTTPS_COUNT remote https URLs in hero section"
    fi
else
    echo "✗ FAIL - Hero section not found"
fi
echo ""

# Check for product title (now in ProductDescription component)
echo "11. Checking product information..."
if curl -s http://127.0.0.1:3001 | grep -q 'pd__title\|hero-product-title'; then
    echo "✓ PASS - Product title element exists"
else
    echo "✗ FAIL - Product title element not found"
fi

if curl -s http://127.0.0.1:3001 | grep -q 'pd__price\|pd__payment-plan'; then
    echo "✓ PASS - Product price and payments exist"
else
    echo "✗ FAIL - Product price and payments not found"
fi
echo ""

# Check for ARIA labels
echo "12. Checking ARIA labels..."
ARIA_COUNT=$(curl -s http://127.0.0.1:3001 | grep -o 'aria-label=' | wc -l || true)
if [ "$ARIA_COUNT" -gt 10 ]; then
    echo "✓ PASS - Multiple ARIA labels found ($ARIA_COUNT)"
else
    echo "✗ FAIL - Insufficient ARIA labels ($ARIA_COUNT)"
fi
echo ""

# Check for section accessibility
echo "13. Checking section accessibility..."
if curl -s http://127.0.0.1:3001 | grep -q 'aria-labelledby="hero-product-title"\|aria-label="Product photographs"'; then
    echo "✓ PASS - Section has proper ARIA labels"
else
    echo "✗ FAIL - Section missing ARIA labels"
fi
echo ""

# Check for focus indicators
echo "14. Checking for focus-visible support..."
FOCUS_COUNT=$(curl -s http://127.0.0.1:3001 | grep -o 'focus-visible' | wc -l || true)
if [ "$FOCUS_COUNT" -gt 5 ]; then
    echo "✓ PASS - Focus-visible styles present ($FOCUS_COUNT)"
else
    echo "✗ FAIL - Focus-visible styles missing ($FOCUS_COUNT)"
fi
echo ""

# Check for semantic fieldsets
echo "15. Checking for semantic form elements..."
FIELDSET_COUNT=$(curl -s http://127.0.0.1:3001 | grep -c '<fieldset' || true)
if [ "$FIELDSET_COUNT" -gt 0 ]; then
    echo "✓ PASS - Semantic fieldsets found ($FIELDSET_COUNT)"
else
    echo "✗ FAIL - Semantic fieldsets not found"
fi
echo ""

# Check for accordion sections (new feature)
echo "16. Checking accordion sections..."
ACCORDION_COUNT=$(curl -s http://127.0.0.1:3001 | grep -c 'pd__accordion-item' || true)
if [ "$ACCORDION_COUNT" -gt 0 ]; then
    echo "✓ PASS - Accordion sections found ($ACCORDION_COUNT)"
else
    echo "✗ FAIL - Accordion sections not found"
fi
echo ""

# Check for benefits section
echo "17. Checking benefits section..."
if curl -s http://127.0.0.1:3001 | grep -q 'pd__benefits\|pd__benefit'; then
    echo "✓ PASS - Benefits section exists"
else
    echo "✗ FAIL - Benefits section not found"
fi
echo ""

# Check for console errors
echo "18. Checking for console errors..."
CONSOLE_ERRORS=$(curl -s http://127.0.0.1:3001 | grep -c 'console.error\|console.warn' || true)
if [ "$CONSOLE_ERRORS" -eq 0 ]; then
    echo "✓ PASS - No console errors found in HTML"
else
    echo "⚠ WARNING - Found $CONSOLE_ERRORS console error references in HTML"
fi
echo ""

echo "========================================================"
echo "QA Complete"
echo "========================================================"
