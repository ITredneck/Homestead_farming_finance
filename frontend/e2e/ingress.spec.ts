import { expect, test } from '@playwright/test';

import { INGRESS_PREFIX } from '../playwright.config';

const HOME = `${INGRESS_PREFIX}/`;
const AREAS = ['Animals', 'Crops', 'Stock', 'Products', 'Sales', 'Money', 'Reports'];

test('works under the ingress path and every request stays under it', async ({ page }) => {
  const outside: string[] = [];
  page.on('request', (request) => {
    const { pathname } = new URL(request.url());
    if (!pathname.startsWith(HOME)) {
      outside.push(pathname);
    }
  });

  await page.goto(HOME);
  for (const name of AREAS) {
    await expect(page.getByRole('link', { name, exact: true })).toBeVisible();
  }

  await page.getByRole('link', { name: 'Settings' }).click();
  await expect(page.getByText('Local Tester')).toBeVisible();
  await expect(page.getByRole('cell', { name: 'e2e', exact: true })).toBeVisible();

  await page.getByRole('link', { name: 'Offline entry test' }).click();
  await expect(page.getByRole('heading', { name: 'Offline entry test' })).toBeVisible();

  expect(outside).toEqual([]);
});

test('home tiles are big enough to tap and fit the screen', async ({ page }, testInfo) => {
  await page.goto(HOME);
  const tile = page.getByRole('link', { name: 'Animals', exact: true });
  await expect(tile).toBeVisible();

  const box = await tile.boundingBox();
  expect(box?.height).toBeGreaterThanOrEqual(120);
  const horizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - window.innerWidth,
  );
  expect(horizontalOverflow).toBeLessThanOrEqual(0);

  await page.screenshot({ path: testInfo.outputPath('home.png'), fullPage: true });
});

test('an entry made offline is stored exactly once after reconnecting', async ({
  page,
  context,
}) => {
  await page.goto(`${HOME}#/spike`);
  await page.getByRole('button', { name: 'Clear test data' }).click();
  await expect(page.getByText('Server: 0 stored')).toBeVisible();

  await context.setOffline(true);
  await page.getByRole('button', { name: 'Add test entry' }).click();
  await page.getByRole('button', { name: 'Add test entry' }).click();
  await expect(page.getByText('2 waiting')).toBeVisible();

  await context.setOffline(false);
  await expect(page.getByText('0 waiting')).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText('Server: 2 stored, 0 duplicates received')).toBeVisible();
});
