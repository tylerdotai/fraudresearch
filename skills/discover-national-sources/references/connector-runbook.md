# Implemented connector runbook

Run from the project directory: `uv run fraudlab ...`. For other working directories use `uv run --project "$HERMES_HOME" fraudlab ...`.

| Command | Actual output/coverage | Must not claim |
|---|---|---|
| `connector cms-hospice` | Catalog-backed public Hospice General Information CSV snapshot | Individual claims, ownership graph or all hospice organizations |
| `connector cms-home-health` | Catalog-backed Home Health Care Agencies CSV snapshot | Dollar payments from relative spending measures |
| `connector nppes --taxonomy hospice --limit 20` | Bounded Type-2 NPI query | Census, licensure or actual billing |
| `connector nppes --taxonomy home-health --state NY --limit 20 --skip 0` | Explicit geographic/taxonomy query | Completeness beyond query window |
| `connector agencies` | USAspending agency reference | Recipient awards, paid invoices or funding nexus |
| `refresh-rules` | Four preserved official program pages | Automatic legal conflict resolution |

CMS metadata endpoint: https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items . The connector discovers one exact title and CSV distribution, then checks provider schema. If title/distribution/columns drift, stop and inspect the new catalog. Do not guess a replacement ID or download URL.

NPPES source contract: https://npiregistry.cms.hhs.gov/api-page . Version 2.1 is documented; limit up to 200 and skip up to 1000 imply a bounded query window. Never loop skip forever or claim all national results from those pages. Large coverage requires a separately evaluated bulk-data workflow, not an invented connector flag.

## Project-isolated bulk and local extraction upgrades

Use `web-search` and `web-extract` for the your configured loopback SearXNG/Crawl4AI services. Source extraction is restricted to public credential-free .gov HTTPS and preserves original response bytes separately from browser-rendered transformations. No CAPTCHA bypass or login sessions. A service health response alone is not useful-content acceptance.

`bulk connector` supports `cms-hospice-chow`, `cms-hospice-owners`, `cms-hospice-enrollments` (including additional NPIs), `oig-leie`, and `oig-reinstatements`. It discovers actual current catalog distributions, retains catalog/download lineage and converts strict CSVs to string-preserving Parquet with parsed-row ordinals. Use explicit `--max-bytes` and `--max-rows` budgets. Current CMS snapshots do not prove historical control; current LEIE and the latest reinstatement supplement do not establish complete historical exclusion intervals. CMS structural Latin-1 decoding is reversible but not confirmed publisher name encoding.

`bulk acquire URL --max-bytes N` streams larger originals; `bulk convert RAW_ID --required COLUMN --max-rows N --max-expanded-bytes N` checks structure and resource budgets. ZIP conversion requires an exact member. Use strict `inspect` commands for legacy SQLite and `bulk query|join|verify` for read-only inspection. No Medicaid bulk connector is implemented merely because HHS documentation is reachable. Do not automatically download multi-GB files or raise old SQLite-import limits.

## Generic acquisition and recovery

`fetch URL --label LABEL --format csv|json|pdf|html|text` is restricted to credential-free public .gov HTTPS GETs. It validates redirect destinations and applies bounded transfers/retries. It is not a hardened network sandbox. `ingest PATH --url URL --label LABEL --format FORMAT` preserves an authorized local original; it does not bypass source access rights.

A source exceeding 20MB or 25,000 rows needs reviewed partitioning/tooling; a failed bounded import is not successful coverage. PDF text extraction may return needs_ocr. Other-source browser inspection is permitted within authorization but does not automatically create a repeatable connector.

Save command, source ID, status, schema, actual records, requested/final URL lineage, extraction state and limits. On 403/auth prompts stop that access path; on transient failures retain receipts and retry only within limits. Never install paid/keyed tooling as an automatic recovery step.
