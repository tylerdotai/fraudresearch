# Design review and acceptance changes

## Observed issues

- The F tile is a placeholder rather than a distinctive logo.
- The footer has too little navigation, platform context and privacy guidance.
- The page lacks JSON-LD, a search-friendly answer summary, a sitemap and a model-readable project brief.
- Movement is mostly primitive defaults; it needs a coherent, restrained motion system.
- Motion, structured claims and component changes need real browser acceptance, not just visual descriptions.

## Required changes before implementation

- A reviewed eagle graphic mark replaces the letter-only header identity; preserve a readable text wordmark.
- A complete footer groups toolkit, research standards, community and platform links. No personal contact information or tip intake.
- Add factual title/description/canonical, social image, WebSite/SoftwareSourceCode/FAQ JSON-LD, sitemap and llms.txt.
- Do not invent ratings, users, rewards, findings, credentials, reviews or government/Nous endorsement.
- Add real shadcn Tabs, Tooltip and Progress components. Install choices and copy behavior must work.
- Progress means page reading progress only, never fraud scanning. Add gentle mascot and scroll-entry motion with a real reduced-motion alternative.
- Recheck desktop/mobile, typography, image load, structured data, keyboard behavior, contrast, overflow and outbound requests.

## SEO, AEO and GEO boundary

These changes improve understandable first-party content and machine-readable facts. They do not guarantee search rank, answer-engine citations, indexing or AI recommendations. GitHub Pages project sites do not control the origin-root robots.txt; page-level robots metadata and the project sitemap are the effective controls this repository can author without changing another site.

Private Playwright screenshots, traces and JSON receipts document the actual runs. Do not publish raw local paths or test data in a design report.

## Observed result

Production desktop and mobile runs passed all 18 browser contracts after the changes. Automated axe checks found no violations under the configured WCAG A/AA tags. The first run caught a copy-button contrast regression caused by a composed Tooltip data-slot and a Progress value not forwarded to Radix; both were corrected and the full suite rerun. This is not a complete human accessibility audit.

Visual review confirmed a graphic eagle/research-lens mark, legible metric hierarchy, distinct government attribution, readable source caveats and grouped footer navigation. Original fictional artwork remains visibly separate from evidence claims. Search markup was parsed in the browser; search ranking and external card rendering were not independently verified.

## Follow-up corrections

Expanded production acceptance passed 24 checks, including a 2560px desktop viewport and mobile. The large F's font bearing is optically compensated so headline ink aligns within two CSS pixels. The panorama now retains its natural aspect ratio between the text-led method and toolkit sections; the character pair closes the page without an adjacent second illustrated hero. Desktop/mobile screenshots confirm readable copy and no panoramic cropping.

The latest-main source/contribution entry points and main-branch build-status link are explicit. GitHub's older per-file last-change badge is distinguished from the current branch status; history is not rewritten to hide a previous failed run. Custom-domain canonical/crawler metadata is generated from one public build URL and was exercised in a real production build.
