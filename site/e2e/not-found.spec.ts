import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('unknown nested addresses return a branded, accessible HTTP 404', async ({ page }) => {
  const response = await page.goto('./missing-page/another-level/');
  expect(response?.status()).toBe(404);
  await expect(page).toHaveTitle('Page not found | AI Against American Fraud');
  await expect(page.getByRole('heading', { name: 'Page not found.', level: 1 })).toBeVisible();
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute('content', 'noindex,follow');
  await expect(page.getByRole('link', { name: 'Return home', exact: true })).toHaveAttribute('href', /^\/(?:[^?#]*\/)?$/);
  for (const image of await page.locator('img').all()) {
    await expect(image).toHaveJSProperty('complete', true);
    expect(await image.evaluate(node => (node as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  }
  expect(await page.locator('script').count()).toBe(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(results.violations).toEqual([]);
  await page.screenshot({ path: `test-results/not-found-${test.info().project.name}.png`, fullPage: true });
  await page.getByRole('link', { name: 'Return home', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1 })).toContainText(/AI against\s*American\s*fraud/i);
});

test('not-found recovery works without JavaScript and does not reflect the URL', async ({ browser, baseURL }, info) => {
  const viewport = info.project.use.viewport || { width: 390, height: 844 };
  const context = await browser.newContext({ javaScriptEnabled: false, viewport });
  try {
    const page = await context.newPage();
    const missing = new URL('missing-no-script/?q=%3Cscript%3Etest-marker%3C%2Fscript%3E', baseURL);
    const response = await page.goto(missing.href);
    expect(response?.status()).toBe(404);
    await expect(page.getByRole('heading', { name: 'Page not found.' })).toBeVisible();
    expect(await page.content()).not.toContain('test-marker');
    await expect(page.getByRole('link', { name: 'View source', exact: true })).toHaveAttribute('href', 'https://github.com/tylerdotai/fraudresearch/tree/main');
    await page.getByRole('link', { name: 'Return home', exact: true }).click();
    expect(new URL(page.url()).pathname).toBe(new URL(baseURL!).pathname);
    await expect(page).toHaveTitle(/AI Against American Fraud/);
  } finally { await context.close(); }
});
