import { defineConfig, devices } from '@playwright/test';

const port = Number(process.env.FRAUDRESEARCH_SITE_PORT || 4179);
const baseURL = `http://127.0.0.1:${port}/fraudresearch/`;
const command = process.env.FRAUDRESEARCH_SITE_PREVIEW === '1' ? 'preview' : 'dev';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'test-results/results.json' }], ['html', { open: 'never' }]],
  use: { baseURL, trace: 'on', screenshot: 'only-on-failure', reducedMotion: 'reduce' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile', use: { ...devices['Desktop Chrome'], viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: { command: `bun run ${command} --host 127.0.0.1 --port ${port} --strictPort`, url: baseURL, reuseExistingServer: false },
});
