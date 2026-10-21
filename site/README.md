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

Production assets use relative URLs, so the same build works at a custom-domain root or a GitHub Pages project path. Local tests serve the root on strict loopback port 4179; override FRAUDRESEARCH_SITE_PORT if needed. They never take over another server. Playwright traces, screenshots, JSON results and the HTML report stay in ignored test-results/ and playwright-report/.

To repeat the same checks against the deployed site without starting a local server, run `FRAUDRESEARCH_SITE_URL=https://tylerdotai.github.io/fraudresearch/ bun run test:e2e`. The no-third-party-request assertion permits only the configured origin, including its protocol and port. Receipts remain local.

Browser tests cover desktop/mobile layouts, source and install links, clipboard, mobile navigation, keyboard entry, real shadcn controls, axe accessibility, artwork loading, copy constraints and absence of automatic third-party requests. Automated accessibility checks are not a full human accessibility audit.

The page includes no forms, uploads, analytics or tip intake. GitHub Pages can log hosting requests. Links to GitHub, Hermes and official government guidance navigate only when the visitor chooses them.

## Numbers and mission

The mission is to help tackle fraud in America with AI through evidence preservation, falsifiable questions and human review. The numbers section reproduces America.gov's partner-agency Total row, not project outcomes: $260.7B uncovered since January 2025, $72.0B stopped per year (annualized), and $58.9B recovered since January 2025. The dated snapshot, original HTML checksum and exact row/line locator are in public/official-context.json. These are publisher claims, not independently audited here. The categories have different measures and periods and must not be added. Update deliberately from a newly preserved source; there is no scheduled scan or live counter.

## Search and answer-engine readability

The site includes a canonical URL, descriptive metadata, social card, JSON-LD for the website/source code/visible FAQ, sitemap, a plain-text llms.txt project brief and a no-JavaScript fallback. No ratings, testimonials or search actions are fabricated. These improve accessible first-party facts, not guaranteed indexing, ranking, rich results or AI citations. llms.txt adoption is optional and engine-dependent.

GitHub Pages project sites cannot control the origin-root robots.txt from this repository. At a custom-domain root, the emitted robots.txt is the origin-level file. Before cutover, a project-path robots.txt is a reference only. No search-console submission or account creation is performed.

The design review covers graphic identity, factual hierarchy, footer navigation, real component behavior, restrained entry/mascot motion and a full reduced-motion alternative. See DESIGN-REVIEW.md. Values are never animated into invented intermediate totals.

## Deployment

The repository workflow builds and tests the static site, then deploys the generated `dist/` artifact to GitHub Pages on an approved main-branch push. Source and dependencies are locked. No live fraud-data scans or scheduled research run in CI. System dependency installs, when present, occur on disposable GitHub-hosted runners, not the operator's workstation.

## Custom-domain migration

The default standalone build targets `https://aiagainstamericanfraud.com/`. Override `PUBLIC_SITE_URL` with an absolute, credential-free HTTPS URL to build for another active address. The checked-in HTML and crawler files are templates: Vite renders their first-party URLs consistently across the canonical, social metadata, inline and standalone JSON-LD, sitemap, robots and llms.txt. Relative asset URLs remain portable.

CI reads the repository's actual configured Pages URL through the pinned configure-pages action, then uses that same URL for the build and browser assertions. It does not prematurely canonicalize an unconnected domain. After DNS ownership, web routing, Pages custom-domain configuration and HTTPS are ready, a push/re-run emits the new origin automatically. A CNAME file alone does not configure an Actions-deployed site.

For the current project address, use `PUBLIC_SITE_URL=https://tylerdotai.github.io/fraudresearch/ bun run build` and pass the same variable with the local production browser command. For a live check, FRAUDRESEARCH_SITE_URL supplies the expected canonical when PUBLIC_SITE_URL is unset. Verify both apex/www redirects and the previous Pages URL after a real cutover. Preserve existing mail/verification DNS records and do not use wildcard records.

Source and contribution entry points explicitly open the latest main branch. Individual GitHub file pages can still show an older commit as that file's last change; this is not a pinned website link or the current branch's build status. The footer links the main-branch build history separately.
