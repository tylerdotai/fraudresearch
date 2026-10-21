import { test, expect } from '@playwright/test';

test('headline ink shares an optical left edge at desktop and mobile sizes', async ({ page }) => {
  if (test.info().project.name === 'desktop') await page.setViewportSize({ width: 2560, height: 1440 });
  await page.goto('./');
  const lefts = await page.locator('h1').evaluate(heading => {
    const ctx = document.createElement('canvas').getContext('2d')!;
    const first = heading.firstChild!;
    const range = document.createRange(); range.selectNodeContents(first);
    return [heading, heading.querySelector('span')!, heading.querySelector('em')!].map((el, index) => {
      const style = getComputedStyle(el);
      ctx.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
      ctx.letterSpacing = style.letterSpacing;
      const text = (index === 0 ? first.textContent! : el.textContent!).trim().toUpperCase();
      const rect = index === 0 ? range.getBoundingClientRect() : el.getBoundingClientRect();
      return rect.left - ctx.measureText(text[0]).actualBoundingBoxLeft;
    });
  });
  expect(Math.max(...lefts) - Math.min(...lefts)).toBeLessThanOrEqual(2);
});

const repo = 'https://github.com/tylerdotai/fraudresearch';

test('source and contribution entry points explicitly follow latest main', async ({ page }) => {
  await page.goto('./');
  await expect(page.getByRole('link', { name: 'View source', exact: true })).toHaveAttribute('href', repo + '/tree/main');
  await expect(page.getByRole('link', { name: 'Contribute on GitHub', exact: true })).toHaveAttribute('href', repo + '/tree/main#help-improve-the-methods');
  await expect(page.getByRole('contentinfo').getByRole('link', { name: 'Latest build status' })).toHaveAttribute('href', repo + '/actions/workflows/verify.yml?query=branch%3Amain');
  const hrefs = await page.locator(`a[href^="${repo}"]`).evaluateAll(nodes => nodes.map(node => (node as HTMLAnchorElement).href));
  for (const href of hrefs) {
    const path = new URL(href).pathname.slice(new URL(repo).pathname.length);
    expect(path).not.toMatch(/^\/commit\//);
    if (/^\/(?:blob|tree)\//.test(path)) expect(path).toMatch(/^\/(?:blob|tree)\/main(?:\/|$)/);
  }
});

test('both images remain, separated by content, without panoramic cropping', async ({ page }) => {
  if (test.info().project.name === 'desktop') await page.setViewportSize({ width: 2560, height: 1440 });
  await page.goto('./');
  const banner = page.getByRole('region', { name: 'Project mission' });
  const image = banner.locator('img');
  await expect(image).toHaveAttribute('src', /patriotic-banner\.webp$/);
  await image.scrollIntoViewIfNeeded();
  await expect(image).toHaveJSProperty('complete', true);
  const structure = await page.evaluate(() => {
    const method = document.querySelector('#method')!;
    const band = document.querySelector('.patriotic-band')!;
    const toolkit = document.querySelector('#toolkit')!;
    const last = document.querySelector('main')!.lastElementChild!;
    const art = band.querySelector('img')!;
    const frame = art.getBoundingClientRect();
    return {
      beforeToolkit: Boolean(band.compareDocumentPosition(toolkit) & Node.DOCUMENT_POSITION_FOLLOWING),
      afterMethod: Boolean(method.compareDocumentPosition(band) & Node.DOCUMENT_POSITION_FOLLOWING),
      communityCloses: last.classList.contains('community-section'),
      displayedRatio: frame.width / frame.height,
      naturalRatio: art.naturalWidth / art.naturalHeight,
      frameWidth: frame.width,
    };
  });
  expect(structure.beforeToolkit).toBe(true);
  expect(structure.afterMethod).toBe(true);
  expect(structure.communityCloses).toBe(true);
  expect(structure.displayedRatio).toBeCloseTo(structure.naturalRatio, 2);
  expect(structure.frameWidth).toBeLessThanOrEqual(1200);
  await expect(page.locator('.community-section img')).toHaveAttribute('src', /community-duo\.webp$/);
  await banner.screenshot({ path: `test-results/mission-placement-${test.info().project.name}.png` });
});
