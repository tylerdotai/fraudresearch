# Architecture

```text
Hermes profile: SOUL + 13 linked research skills
        |
        +--> profile-local web adapter --> uv-managed fraudlab process
        |                                  |-- configured loopback SearXNG
        |                                  |-- configured loopback Crawl4AI
        |                                  +-- bounded official .gov originals
        |
        +--> operator-driven CLI
                 |-- SQLite sources / records / provenance events
                 |-- immutable bulk originals -> strict CSV -> Parquet
                 |-- bounded exact queries and joins
                 +-- private case drafts and attachment manifests
```

All runtime evidence is outside the checkout by default. Bulk/Parquet data are separate from the case SQLite store; do not confuse their counts or verification scopes. Source IDs and dataset IDs are content-derived; preserve returned values rather than guessing identifiers.

## Limits

- Ordinary structured imports: at most 20MB and 25,000 rows per source.
- Bulk acquisition: explicit operator byte budget, hard maximum 5GB.
- Bulk conversion: explicit row/expanded-byte budgets, supported strict encodings and selected ZIP members.
- DuckDB: 512MB memory, two threads, 1GB scratch-spill cap, 120-second query interrupt.
- Query/join output: at most 1,000 rows/pairs, with total and truncation metadata.
- No arbitrary user SQL, network-reading SQL or automatic extension installation.
- No automatic schedules, submission, messaging, public servers or source-document execution.

Original hashes and exact quote locators detect certain integrity/citation problems. They do not establish meaning, criminal conduct, historical relationships, substantive originality or legal eligibility. A privileged attacker who changes files and trusted metadata is outside this integrity model.

The .gov/public-address checks and redirect validation are not a hardened network sandbox. Browser subresources need their own host-level controls. Services and model providers have independent security/data policies.
