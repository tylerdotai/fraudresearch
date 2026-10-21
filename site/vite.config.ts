import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath, URL } from 'node:url';
import { existsSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import type { IncomingMessage, ServerResponse } from 'node:http';

const templateURL = 'https://tylerdotai.github.io/fraudresearch/';
const siteURL = new URL(process.env.PUBLIC_SITE_URL ?? 'https://aiagainstamericanfraud.com/');
if (siteURL.protocol !== 'https:' || siteURL.username || siteURL.password || siteURL.search || siteURL.hash) {
  throw new Error('PUBLIC_SITE_URL must be a credential-free HTTPS site URL');
}
const canonicalURL = siteURL.href.replace(/\/?$/, '/');
const render = (text: string) => text.replaceAll(templateURL, canonicalURL).replaceAll('__SITE_PATH__', siteURL.pathname.replace(/\/?$/, '/'));
const metadataFiles = ['llms.txt', 'robots.txt', 'sitemap.xml', 'structured-data.json', '404.html'];

function canonicalMetadata(): Plugin {
  let root = '';
  let output = '';
  const notFound = (directories: string[], dev: boolean) => (request: IncomingMessage, response: ServerResponse, next: () => void) => {
    let pathname: string;
    try { pathname = decodeURIComponent(new URL(request.url ?? '/', 'http://localhost').pathname); }
    catch { response.statusCode = 400; response.end('Invalid address'); return; }
    if (pathname === '/' || (dev && pathname.startsWith('/@'))) return next();
    const found = directories.some(directory => {
      const candidate = resolve(directory, '.' + pathname);
      return candidate.startsWith(directory + sep) && existsSync(candidate) && statSync(candidate).isFile();
    });
    if (found) return next();
    response.statusCode = 404;
    response.setHeader('Content-Type', 'text/html; charset=utf-8');
    response.setHeader('Cache-Control', 'no-store');
    const html = render(readFileSync(resolve(root, 'public', '404.html'), 'utf8'));
    response.end(request.method === 'HEAD' ? undefined : html);
  };
  return {
    name: 'canonical-metadata',
    configResolved(config) { root = config.root; output = resolve(root, config.build.outDir); },
    transformIndexHtml(html) { return render(html); },
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const name = (request.url ?? '').split('?')[0].slice(1);
        if (!metadataFiles.includes(name)) return next();
        const type = name.endsWith('.json') ? 'application/json' : name.endsWith('.xml') ? 'application/xml' : name.endsWith('.html') ? 'text/html' : 'text/plain';
        response.setHeader('Content-Type', `${type}; charset=utf-8`);
        response.end(render(readFileSync(resolve(root, 'public', name), 'utf8')));
      });
      server.middlewares.use(notFound([root, resolve(root, 'public')], true));
    },
    configurePreviewServer(server) { server.middlewares.use(notFound([output], false)); },
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
