import { test, expect } from '@playwright/test';

const base = 'https://tylerdotai.github.io/fraudresearch/';

test('graphic identity, complete footer and mission are present', async ({ page }) => {
  await page.goto('./');
  await expect(page.getByRole('link', { name: 'FraudResearch home' }).locator('img')).toBeVisible();
  const footer = page.getByRole('contentinfo');
  for (const name of ['Toolkit', 'Research standards', 'Community', 'Platform']) {
    await expect(footer.getByRole('navigation', { name, exact: true })).toBeAttached();
  }
  await expect(page.getByText('Our mission is to help tackle fraud in America with AI', { exact: false })).toBeVisible();
});

test('official figures preserve government labels and are not toolkit results', async ({ page, request }) => {
  const result = await request.get('./official-context.json');
  expect(result.ok()).toBe(true);
  const context = await result.json();
  expect(context.source_url).toBe('https://america.gov/fraud');
  expect(context.original_sha256).toMatch(/^[a-f0-9]{64}$/);
  expect(context.metrics).toHaveLength(3);
  await page.goto('./');
  for (const metric of context.metrics) await expect(page.getByText(metric.display, { exact: true })).toBeVisible();
  await expect(page.getByText('Not results from FraudResearch.', { exact: false })).toBeVisible();
});

test('canonical, social, structured data and first-party briefs are truthful', async ({ page, request }) => {
  await page.goto('./');
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', base);
  await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', base + 'social-card.webp');
  const graph = await page.locator('script[type="application/ld+json"]').evaluateAll((nodes) => nodes.flatMap(node => JSON.parse(node.textContent || '{}')['@graph'] || []));
  expect(graph.some(node => node['@type'] === 'WebSite')).toBe(true);
  expect(graph.some(node => node['@type'] === 'SoftwareSourceCode')).toBe(true);
  const faq = graph.find(node => node['@type'] === 'FAQPage');
  expect(faq.mainEntity).toHaveLength(5);
  expect(JSON.stringify(graph)).not.toMatch(/aggregateRating|reviewCount|GovernmentOrganization/);
  for (const name of ['llms.txt', 'robots.txt', 'sitemap.xml']) {
    const response = await request.get('./' + name);
    expect(response.ok()).toBe(true);
  }
});

test('real shadcn tabs and reading progress work with reduced motion', async ({ page }) => {
  await page.goto('./');
  await page.getByRole('tab', { name: 'Python workbench' }).click();
  await expect(page.getByRole('tabpanel')).toContainText('uv sync');
  await page.getByRole('tab', { name: 'Hermes profile' }).click();
  await expect(page.getByRole('tabpanel')).toContainText('hermes profile install');
  await page.getByRole('contentinfo').scrollIntoViewIfNeeded();
  const progress = page.getByRole('progressbar', { name: 'Page reading progress' });
  await expect.poll(async () => Number(await progress.getAttribute('aria-valuenow'))).toBeGreaterThan(70);
  const motion = await page.locator('.mascot-image').evaluate(node => getComputedStyle(node).animationName);
  expect(motion).toBe('none');
});
