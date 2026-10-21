# AI Against American Fraud: the public website

A static React/Vite landing page for the FraudResearch toolkit, deployed through GitHub Pages.

## Design and components

The site uses genuine shadcn/ui New York components: Button, Badge, Accordion, Sheet, Separator, Tabs, Tooltip and Progress. Their source was retrieved from the official registry. Utility import aliases were adapted, and Progress was corrected to forward its value to Radix for accurate accessible progress. Radix supplies the interactive primitives. See SHADCN-LICENSE.txt.

The visual system combines flag red, navy, warm ivory, oversized civic typography and four coordinated fictional illustrations: the eagle, the Nous-inspired adult character, the community duo and the panoramic backdrop. Rendered copy contains no em dashes or emojis. No charts, fraud totals, endorsements or testimonials are invented.

The Nous girl source mark comes from the official Hermes repository. Its editor-specific metadata was removed while preserving rendering geometry. NOUS-LICENSE.txt preserves the upstream MIT notice. Platform branding and community artwork do not imply Nous Research or government endorsement. Trademark rights remain with their owners.

Artwork generation used the installed Hermes OpenAI Codex-auth image provider. The rendering engine is backend-managed; the selected model label does not prove which engine generated an image. Generated images are fictional brand illustrations, not evidence. Public files were re-encoded from fresh RGB pixels with no inherited metadata. Source URLs, transforms and hashes are in artwork-provenance.json. Private generation receipts, original cache paths and request IDs are not distributed.

## Build and test

Requires Bun 1.3.14 and a compatible Node runtime (22.12+ or current supported release).

```bash
bun install --frozen-lockfile
bun run build
bunx playwright install chromium
FRAUDRESEARCH_SITE_PREVIEW=1 bun run test:e2e
```

The production base path is `/fraudresearch/`. Tests start a strict loopback server on port 4179; override FRAUDRESEARCH_SITE_PORT if needed. They never take over another server. Playwright traces, screenshots, JSON results and the HTML report stay in ignored test-results/ and playwright-report/.

To repeat the same checks against the deployed site without starting a local server, run `FRAUDRESEARCH_SITE_URL=https://tylerdotai.github.io/fraudresearch/ bun run test:e2e`. The no-third-party-request assertion permits only the configured origin, including its protocol and port. Receipts remain local.

Browser tests cover desktop/mobile layouts, source and install links, clipboard, mobile navigation, keyboard entry, real shadcn controls, axe accessibility, artwork loading, copy constraints and absence of automatic third-party requests. Automated accessibility checks are not a full human accessibility audit.

The page includes no forms, uploads, analytics or tip intake. GitHub Pages can log hosting requests. Links to GitHub, Hermes and official government guidance navigate only when the visitor chooses them.

## Numbers and mission

The mission is to help tackle fraud in America with AI through evidence preservation, falsifiable questions and human review. The numbers section reproduces America.gov's partner-agency Total row, not project outcomes: $260.7B uncovered since January 2025, $72.0B stopped per year (annualized), and $58.9B recovered since January 2025. The dated snapshot, original HTML checksum and exact row/line locator are in public/official-context.json. These are publisher claims, not independently audited here. The categories have different measures and periods and must not be added. Update deliberately from a newly preserved source; there is no scheduled scan or live counter.

## Search and answer-engine readability

The site includes a canonical URL, descriptive metadata, social card, JSON-LD for the website/source code/visible FAQ, sitemap, a plain-text llms.txt project brief and a no-JavaScript fallback. No ratings, testimonials or search actions are fabricated. These improve accessible first-party facts, not guaranteed indexing, ranking, rich results or AI citations. llms.txt adoption is optional and engine-dependent.

GitHub Pages project sites cannot control the origin-root robots.txt from this repository. The project-path robots.txt is a reference, not an origin-wide policy. Page-level robots metadata and the project sitemap are authored here without changing another website. No search-console submission or account creation is performed.

The design review covers graphic identity, factual hierarchy, footer navigation, real component behavior, restrained entry/mascot motion and a full reduced-motion alternative. See DESIGN-REVIEW.md. Values are never animated into invented intermediate totals.

## Deployment

The repository workflow builds and tests the static site, then deploys the generated `dist/` artifact to GitHub Pages on an approved main-branch push. Source and dependencies are locked. No live fraud-data scans or scheduled research run in CI. System dependency installs, when present, occur on disposable GitHub-hosted runners, not the operator's workstation.
