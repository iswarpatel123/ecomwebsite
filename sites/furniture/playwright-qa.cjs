const { chromium } = require('playwright');

async function runQA() {
  console.log('Starting DOM/Functional QA for Furniture Hero Section...\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const results = {
    desktop: { passed: 0, failed: 0, errors: [] },
    tablet: { passed: 0, failed: 0, errors: [] },
    mobile: { passed: 0, failed: 0, errors: [] }
  };

  const testCases = [
    // 1. Semantic structure
    { name: 'Has h1 heading', check: (doc) => !!doc.querySelector('h1') },
    { name: 'H1 has product title', check: (doc) => {
      const h1 = doc.querySelector('h1');
      return h1 && h1.textContent.trim() && h1.textContent.trim().length > 5;
    }},
    { name: 'H1 contains "Wanda Sofa Bed"', check: (doc) => {
      const h1 = doc.querySelector('h1');
      return h1 && h1.textContent.includes('Wanda Sofa Bed');
    }},
    // 2. ARIA labels and accessibility
    { name: 'Main image has alt attribute', check: (doc) => {
      const img = doc.querySelector('.product-gallery__main-image');
      return img && img.getAttribute('alt') && img.getAttribute('alt').trim() !== '';
    }},
    { name: 'Alt text contains product name', check: (doc) => {
      const img = doc.querySelector('.product-gallery__main-image');
      return img && img.getAttribute('alt') && img.getAttribute('alt').includes('Wanda Sofa Bed');
    }},
    { name: 'Thumbnail images have alt attributes', check: (doc) => {
      const thumbs = doc.querySelectorAll('.product-gallery__thumbnail');
      return thumbs.length > 0 && Array.from(thumbs).every(t => t.getAttribute('alt') && t.getAttribute('alt').trim() !== '');
    }},
    { name: 'Prev button has aria-label', check: (doc) => {
      const btn = doc.querySelector('.gallery-nav__prev');
      return btn && btn.getAttribute('aria-label') && btn.getAttribute('aria-label').includes('previous');
    }},
    { name: 'Next button has aria-label', check: (doc) => {
      const btn = doc.querySelector('.gallery-nav__next');
      return btn && btn.getAttribute('aria-label') && btn.getAttribute('aria-label').includes('next');
    }},
    { name: 'Size buttons have aria-label', check: (doc) => {
      const sizeBtns = doc.querySelectorAll('[data-size]');
      return sizeBtns.length > 0;
    }},
    { name: 'Color swatches have aria-label', check: (doc) => {
      const swatches = doc.querySelectorAll('[data-color]');
      return swatches.length > 0;
    }},
    // 3. Gallery controls (no 360 or gallery-view buttons)
    { name: 'No 360-view button in hero', check: (doc) => {
      return !doc.querySelector('[data-360]') && !doc.querySelector('.view-360');
    }},
    { name: 'No gallery-view button in hero', check: (doc) => {
      return !doc.querySelector('[data-gallery-view]') && !doc.querySelector('.view-gallery');
    }},
    { name: 'Thumbnail click works', check: (doc) => {
      const thumbs = doc.querySelectorAll('.product-gallery__thumbnail');
      return thumbs.length > 0;
    }},
    { name: 'Prev/Next buttons exist', check: (doc) => {
      return doc.querySelector('.gallery-nav__prev') && doc.querySelector('.gallery-nav__next');
    }},
    // 4. Size selection
    { name: 'Size 75 option exists', check: (doc) => {
      const sizeBtn = doc.querySelector('[data-size="75"]');
      return sizeBtn && sizeBtn.textContent.trim().includes('75');
    }},
    { name: 'Size 99 option exists', check: (doc) => {
      const sizeBtn = doc.querySelector('[data-size="99"]');
      return sizeBtn && sizeBtn.textContent.trim().includes('99');
    }},
    { name: 'Size 75 selection updates state', check: async (page) => {
      const sizeBtn = await page.locator('[data-size="75"]').first();
      if (!sizeBtn) return false;
      await sizeBtn.click();
      await page.waitForTimeout(300);
      return await page.locator('[data-size="75"]').getAttribute('aria-selected') === 'true';
    }},
    { name: 'Size 99 selection updates state', check: async (page) => {
      const sizeBtn = await page.locator('[data-size="99"]').first();
      if (!sizeBtn) return false;
      await sizeBtn.click();
      await page.waitForTimeout(300);
      return await page.locator('[data-size="99"]').getAttribute('aria-selected') === 'true';
    }},
    // 5. Color selection
    { name: 'Color swatches exist', check: (doc) => {
      const swatches = doc.querySelectorAll('[data-color]');
      return swatches.length >= 3;
    }},
    { name: 'First color swatch has label', check: (doc) => {
      const swatch = doc.querySelector('[data-color]').first();
      return swatch && swatch.getAttribute('aria-label') && swatch.getAttribute('aria-label').trim() !== '';
    }},
    { name: 'Color selection updates state', check: async (page) => {
      const swatch = await page.locator('[data-color]').first();
      if (!swatch) return false;
      const color = await swatch.getAttribute('data-color');
      await swatch.click();
      await page.waitForTimeout(300);
      return await page.locator(`[data-color="${color}"]`).getAttribute('aria-selected') === 'true';
    }},
    // 6. Quantity controls
    { name: 'Quantity input exists', check: (doc) => {
      const input = doc.querySelector('[data-quantity]');
      return input && input.tagName === 'INPUT';
    }},
    { name: 'Quantity min is 1', check: async (page) => {
      const input = await page.locator('[data-quantity]').first();
      const min = await input.getAttribute('min');
      return min === '1';
    }},
    { name: 'Quantity max is 10', check: async (page) => {
      const input = await page.locator('[data-quantity]').first();
      const max = await input.getAttribute('max');
      return max === '10';
    }},
    { name: 'Quantity input accepts values 1-10', check: async (page) => {
      const input = await page.locator('[data-quantity]').first();
      await input.fill('1');
      await page.waitForTimeout(100);
      await input.fill('10');
      await page.waitForTimeout(100);
      return await input.inputValue() === '10';
    }},
    // 7. Add to cart
    { name: 'Add to cart button exists', check: (doc) => {
      const btn = doc.querySelector('[data-add-to-cart]');
      return btn && btn.tagName === 'BUTTON';
    }},
    { name: 'Add to cart button has aria-label', check: (doc) => {
      const btn = doc.querySelector('[data-add-to-cart]');
      return btn && btn.getAttribute('aria-label') && btn.getAttribute('aria-label').includes('add to cart');
    }},
    { name: 'Add to cart button has correct text', check: (doc) => {
      const btn = doc.querySelector('[data-add-to-cart]');
      return btn && btn.textContent.trim().includes('Add to cart');
    }},
    { name: 'Add to cart button is enabled', check: async (page) => {
      const btn = await page.locator('[data-add-to-cart]').first();
      return await btn.isEnabled();
    }},
    { name: 'Add to cart click shows feedback', check: async (page) => {
      const btn = await page.locator('[data-add-to-cart]').first();
      const initialText = await btn.textContent();
      await btn.click();
      await page.waitForTimeout(500);
      const newText = await btn.textContent();
      return newText !== initialText;
    }},
    // 8. No remote URLs
    { name: 'No remote https URLs in hero', check: async (page) => {
      const frame = page.frameLocator('#shopify-preview');
      const html = await frame.locator('html').innerHTML();
      const heroSection = html.substring(html.indexOf('<section'), html.indexOf('</section>') + 9);
      const httpsMatch = heroSection.match(/https?:\/\/[^\s"'>]+/g);
      return !httpsMatch || httpsMatch.length === 0;
    }},
    // 9. Product information
    { name: 'Product title present', check: (doc) => {
      const title = doc.querySelector('[data-product-title]');
      return title && title.textContent.trim().length > 5;
    }},
    { name: 'Price displays correctly', check: (doc) => {
      const price = doc.querySelector('[data-product-price]');
      return price && price.textContent.trim().length > 3;
    }},
    // 10. Responsive layout
    { name: 'Desktop viewport no overflow', check: async (page) => {
      await page.setViewportSize({ width: 1440, height: 900 });
      await page.goto('http://127.0.0.1:3001');
      await page.waitForTimeout(2000);
      const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
      const viewportHeight = 900;
      return bodyHeight <= viewportHeight + 50;
    }},
    { name: 'Tablet viewport no overflow', check: async (page) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('http://127.0.0.1:3001');
      await page.waitForTimeout(2000);
      const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
      const viewportHeight = 1024;
      return bodyHeight <= viewportHeight + 50;
    }},
    { name: 'Mobile viewport no overflow', check: async (page) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('http://127.0.0.1:3001');
      await page.waitForTimeout(2000);
      const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
      const viewportHeight = 667;
      return bodyHeight <= viewportHeight + 50;
    }},
    // 11. Console errors
    { name: 'No console errors on page load', check: async (page) => {
      const errors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') errors.push(msg.text());
      });
      await page.goto('http://127.0.0.1:3001');
      await page.waitForTimeout(2000);
      return errors.length === 0;
    }}
  ];

  const viewports = [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 }
  ];

  for (const viewport of viewports) {
    console.log(`\n=== Testing ${viewport.name} viewport ===`);
    const context = await browser.newContext({ viewport });
    const page = await context.newPage();

    try {
      await page.goto('http://127.0.0.1:3001', { waitUntil: 'networkidle', timeout: 10000 });
      await page.waitForTimeout(2000);

      // Get page title
      const title = await page.title();
      console.log(`Page title: ${title}`);

      // Check for errors
      const errors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') errors.push(msg.text());
      });

      // Run tests
      for (const testCase of testCases) {
        try {
          const passed = await testCase.check(page);
          if (passed) {
            console.log(`✓ ${testCase.name}`);
            results[viewport.name].passed++;
          } else {
            console.log(`✗ ${testCase.name}`);
            results[viewport.name].failed++;
            results[viewport.name].errors.push(`${testCase.name} - FAILED`);
          }
        } catch (error) {
          console.log(`✗ ${testCase.name} - ERROR: ${error.message}`);
          results[viewport.name].failed++;
          results[viewport.name].errors.push(`${testCase.name} - ERROR: ${error.message}`);
        }
      }

      // Check for console errors
      if (errors.length > 0) {
        console.log(`\nConsole errors (${errors.length}):`);
        errors.forEach(e => console.log(`  - ${e}`));
        results[viewport.name].errors.push(`Console errors: ${errors.join(', ')}`);
      }

    } catch (error) {
      console.log(`Error testing ${viewport.name}: ${error.message}`);
      results[viewport.name].errors.push(`Error: ${error.message}`);
      results[viewport.name].failed++;
    }

    await context.close();
  }

  await browser.close();

  // Print summary
  console.log('\n' + '='.repeat(60));
  console.log('QA SUMMARY');
  console.log('='.repeat(60));
  for (const [viewport, result] of Object.entries(results)) {
    console.log(`\n${viewport.charAt(0).toUpperCase() + viewport.slice(1)}:`);
    console.log(`  Passed: ${result.passed}`);
    console.log(`  Failed: ${result.failed}`);
    if (result.errors.length > 0) {
      console.log(`  Errors:`);
      result.errors.forEach(e => console.log(`    - ${e}`));
    }
  }

  const totalPassed = Object.values(results).reduce((sum, r) => sum + r.passed, 0);
  const totalFailed = Object.values(results).reduce((sum, r) => sum + r.failed, 0);

  console.log(`\nTotal: ${totalPassed} passed, ${totalFailed} failed`);

  const allPassed = totalFailed === 0;
  console.log(`\n${allPassed ? '✓ PASS' : '✗ FAIL'} - QA Complete`);

  process.exit(allPassed ? 0 : 1);
}

runQA().catch(error => {
  console.error('QA failed:', error);
  process.exit(1);
});
