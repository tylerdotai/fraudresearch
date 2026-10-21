# Setup

## Workbench

Read `.env.example`. Install uv and Python 3.11+ using their official instructions. Run `uv sync --frozen --group dev` in the checkout. This creates only a project environment; it does not modify Hermes's Python environment.

`fraudlab --home PRIVATE_DIRECTORY init` chooses an explicit evidence store. Without an override, `XDG_DATA_HOME/fraudresearch` or `~/.local/share/fraudresearch` is used. The workbench does not load `.env` automatically. Do not put credentials in project source.

Scratch uses the operator's TMPDIR when supplied; otherwise it creates a private `scratch/` below the default data home. Data retention/cleanup is the operator's responsibility. Keep demo and real research stores separate.

## Optional local web services

Supply your own SearXNG and Crawl4AI installation. This project neither starts servers nor modifies containers. Review upstream installation/security instructions:
- https://docs.searxng.org/
- https://docs.crawl4ai.com/

Create `~/.config/fraudresearch/services.json`, or `$XDG_CONFIG_HOME/fraudresearch/services.json`:

```json
{
  "searxng_url": "http://127.0.0.1:8080",
  "crawl4ai_url": "http://127.0.0.1:11235"
}
```

These are example ports, not automatically discovered or promised services. Replace them with your actual loopback mappings. URLs must be credential-free HTTP on literal `127.0.0.1`, with an explicit port and no path/query/fragment. The JSON file is settings, not a credential store. Do not publish it.

SearXNG must permit JSON search and the configured Google/Bing engines must return useful results. Crawl4AI must support its `/crawl` BrowserConfig/CrawlerRunConfig API. Service health alone is not acceptance: inspect actual relevant results and extracted source content.

```bash
uv run fraudlab web-search 'Medicare hospice'
uv run fraudlab web-extract https://www.justice.gov/fraud/whistleblower
```

`web-extract` requires configured rendering service settings even for its PDF path. PDF transformation uses an existing `pdftotext` executable; the standalone `fetch --format pdf` route does not need Crawl4AI. Scan-only material requiring OCR fails explicitly or is marked `needs_ocr`; no text is invented. No OCR is installed automatically.

## Hermes

Install the distribution using the README command and select your own model with `hermes -p fraudresearch-starter setup`. Sync the installed workbench with uv before using the provider. The distribution ships only generic web/provider settings and an explicit plugin selection. Model access may cost money; no subscription or paid API is included.

Start a fresh chat after installation so the provider registry is rebuilt. General terminal/browser permissions remain those of the operator and Hermes. This persona is not a security sandbox and does not change approval controls. No cron or messaging configuration ships.

Updates use `hermes profile update fraudresearch-starter`. Review upstream diffs before updating. Hermes normally preserves locally tuned config; consult its current profile-distribution documentation rather than forcing replacement of your settings.

## Current platform scope

Initial verification is Linux. Python/uv are portable, but native tools, paths, process permissions and rendering services need platform-specific acceptance. Do not describe macOS/Windows as tested without their own receipts.
