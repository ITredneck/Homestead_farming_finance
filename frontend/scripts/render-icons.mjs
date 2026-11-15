// Renders the app store icon and logo PNGs from the SVG artwork.
// Usage: pnpm icons   (needs the Playwright Chromium browser: pnpm exec playwright install chromium)
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { chromium } from '@playwright/test';

const frontend = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const brand = path.join(frontend, 'src', 'assets', 'brand');
const app = path.join(frontend, '..', 'homestead_finance');

const targets = [
  { svg: 'icon.svg', png: 'icon.png', width: 128, height: 128 },
  { svg: 'logo.svg', png: 'logo.png', width: 250, height: 100 },
];

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  for (const { svg, png, width, height } of targets) {
    await page.setViewportSize({ width, height });
    const markup = readFileSync(path.join(brand, svg), 'utf8');
    await page.setContent(`<body style="margin:0;background:transparent">${markup}</body>`);
    await page.locator('svg').screenshot({ path: path.join(app, png), omitBackground: true });
    console.log(`Rendered ${png} (${width}x${height})`);
  }
} finally {
  await browser.close();
}
