# Privacy and release boundary

## What is distributed

Only the files named in `release-files.json`, plus their SHA256 manifest. No identifying records, real cases, evidence databases, acquired documents, prior investigation notes, owner identity, sessions, memories, credentials or live service configuration are intentionally included. The public hosting account remains visible by design; that is not anonymous publication.

Release construction starts from an empty directory and copies named files. `.gitignore` is defense in depth, not an export policy. Pattern scanning cannot identify every form of PII or confidential context; review prompts, examples, metadata, Git history, authorship and final archive bytes manually.

The only raster exceptions are four explicitly named, visually reviewed fictional brand illustrations. Each was re-encoded from fresh RGB pixels. The release gate rejects EXIF, XMP, ICC, animation and unknown WebP chunks, even when an injected file's checksum is refreshed. No arbitrary binary files are permitted. The Nous SVG was stripped of editor metadata; upstream license notices are retained. These checks do not detect every possible form of embedded or visible information, so visual review remains necessary.

## Runtime data flows

| Action | Receives data | Stores data |
|---|---|---|
| Offline synthetic demo | Local Python CLI only | Chosen private synthetic store |
| Official-source connector | Source website receives a request/IP and relevant query parameters | Originals, receipts and derived rows in private data home |
| Local search | Loopback SearXNG receives the query; its upstream engines can also receive it | Runtime/service logs depend on operator configuration |
| HTML extraction | Loopback Crawl4AI receives a URL; browser contacts websites and subresources | Original, renderer response, rendered text and hashes in private data home |
| Hermes research | Selected model provider can receive prompts, tool output and context | Hermes's own profile/session storage and provider policies apply |
| Public README images | GitHub/image-proxy and badge services may receive image requests | Their own logging policies apply |

Do not put patient, child, family, tipster or unnecessary subject identifiers in prompts or public contributions. Public-source records can still identify people. No automatic PII anonymizer is claimed. Local evidence storage is not a zero-egress guarantee.

## Storage and access

The CLI sets a restrictive creation mask; evidence directories are created privately. These are not encryption, access-control isolation, tamper-proof custody or a backup system. Existing directory permissions, file-system ACLs, other user processes and the host environment still matter. Protect and back up the store appropriately.

The workbench's strict inspect routes avoid evidence-store writes. Ordinary status/verify and legacy analysis commands can initialize structures or append events. DuckDB can create private scratch spill. Use the command-effects reference before a no-write review.

## Release checklist

Build using `uv run python scripts/release.py --output /path/outside-checkout/fraudresearch.zip`. Extract into an empty directory, run `scripts/privacy_check.py --root EXTRACTED_DIRECTORY`, and review all included text. The file scanner rejects unexpected paths, symlinks, checksum changes and selected private/secret patterns. Exact synthetic negative fixtures in the test source are narrowly exempted so the rejection tests can ship.

Optional local-only `FRAUDRESEARCH_PRIVATE_MARKERS` is a JSON list of private review strings; never store those values in repository files. `FRAUDRESEARCH_PUBLIC_ACCOUNT` can identify the expressly approved public GitHub account so repository URLs are not mistaken for prohibited personal references. Neither setting is bundled or required by normal users.

Scan the actual staged Git tree and archive, not just a working directory. Use a generic release author and noreply commit email. Never push private history first and try to redact it later.
