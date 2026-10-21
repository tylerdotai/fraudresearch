import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath, URL } from 'node:url';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const templateURL = 'https://tylerdotai.github.io/fraudresearch/';
const siteURL = new URL(process.env.PUBLIC_SITE_URL ?? 'https://aiagainstamericanfraud.com/');
if (siteURL.protocol !== 'https:' || siteURL.username || siteURL.password || siteURL.search || siteURL.hash) {
  throw new Error('PUBLIC_SITE_URL must be a credential-free HTTPS site URL');
}
const canonicalURL = siteURL.href.replace(/\/?$/, '/');
const render = (text: string) => text.replaceAll(templateURL, canonicalURL);
const metadataFiles = ['llms.txt', 'robots.txt', 'sitemap.xml', 'structured-data.json'];

function canonicalMetadata(): Plugin {
  let root = '';
  let output = '';
  return {
    name: 'canonical-metadata',
    configResolved(config) { root = config.root; output = resolve(root, config.build.outDir); },
    transformIndexHtml(html) { return render(html); },
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const name = (request.url ?? '').split('?')[0].slice(1);
        if (!metadataFiles.includes(name)) return next();
        const type = name.endsWith('.json') ? 'application/json' : name.endsWith('.xml') ? 'application/xml' : 'text/plain';
        response.setHeader('Content-Type', `${type}; charset=utf-8`);
        response.end(render(readFileSync(resolve(root, 'public', name), 'utf8')));
      });
    },
    writeBundle() {
      for (const name of metadataFiles) {
        writeFileSync(resolve(output, name), render(readFileSync(resolve(root, 'public', name), 'utf8')));
      }
    },
  };
}

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss(), canonicalMetadata()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
});
