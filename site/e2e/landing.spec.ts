import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const repo = 'https://github.com/tylerdotai/fraudresearch';

test('landing page presents a truthful, usable research toolkit', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('./');
  await expect(page).toHaveTitle(/AI Against American Fraud.*FraudResearch/);
  await expect(page.locator('h1')).toHaveCount(1);
  await expect(page.getByRole('heading', { level: 1 })).toContainText(/AI against\s*American\s*fraud/i);
  await expect(page.getByRole('img', { name: /Eagle investigator mascot/ })).toBeVisible();
  await expect(page.getByText('Not affiliated with the U.S. government.', { exact: false })).toBeVisible();
  await expect(page.getByRole('link', { name: 'View source', exact: true })).toHaveAttribute('href', repo);
  const body = await page.locator('body').innerText();
  expect(body).not.toContain('\u2014');
  expect(body).not.toMatch(/\p{Extended_Pictographic}/u);
  expect(body).not.toMatch(/guaranteed (?:reward|recovery)|fraud detected|trusted by \d/i);
  for (const image of await page.locator('img').all()) {
    await image.scrollIntoViewIfNeeded();
    await expect(image).toHaveJSProperty('complete', true);
  }
  expect(await page.locator('img').evaluateAll((images) => images.every((image) => image instanceof HTMLImageElement && image.complete && image.naturalWidth > 0))).toBe(true);
  expect(errors).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `test-results/landing-${test.info().project.name}.png`, fullPage: true });
});

test('installation command can be copied and FAQ uses accessible components', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('./');
  await page.getByRole('button', { name: 'Copy install command' }).click();
  await expect(page.getByRole('status')).toContainText('Copied');
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain('hermes profile install github.com/tylerdotai/fraudresearch');
  const question = page.getByRole('button', { name: 'Does this software determine whether someone committed fraud?' });
  await question.click();
  await expect(question).toHaveAttribute('aria-expanded', 'true');
  await expect(page.getByText('No. It organizes research and checks structure, not guilt.', { exact: false })).toBeVisible();
  await expect(page.locator('[data-slot="accordion"]')).toHaveCount(1);
  expect(await page.locator('[data-slot="button"]').count()).toBeGreaterThan(2);
});

test('navigation supports mobile and keyboard access', async ({ page }) => {
  await page.goto('./');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  if (test.info().project.name === 'mobile') {
    await page.getByRole('button', { name: 'Open navigation' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('dialog').getByRole('link', { name: 'The method' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page).toHaveURL(/#method$/);
  }
});

test('has no automatically detectable accessibility violations', async ({ page }) => {
  await page.goto('./');
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(results.violations).toEqual([]);
});

test('is static and does not contact third-party services on load', async ({ page, baseURL }) => {
  if (!baseURL) throw new Error('A configured baseURL is required');
  const permittedOrigin = new URL(baseURL).origin;
  const external: string[] = [];
  page.on('request', (request) => {
    const url = new URL(request.url());
    if (url.protocol.startsWith('http') && url.origin !== permittedOrigin) external.push(url.hostname);
  });
  await page.goto('./');
  await page.waitForLoadState('networkidle');
  expect(external).toEqual([]);
  expect(await page.evaluate(() => document.cookie)).toBe('');
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
});
