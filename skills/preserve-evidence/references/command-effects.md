# Command effects and strict read-only work

Do not infer side effects from a command's name. The current analysis commands deliberately append provenance events. That is appropriate during an authorized investigation, but violates an instruction to leave the evidence store unchanged.

## Current effects matrix

| Operation | Reads | Writes/effects | Strict evidence-store read-only? |
|---|---|---|---|
| `fraudlab --help`, subcommand `--help` | CLI definitions | Exits before opening store | Yes |
| `status`, `sources`, `records`, `verify`, `match`, `case check`, `case list` | Existing evidence/metadata | CLI initializes store/schema and some directories; no analysis event in these handlers | Only logically read-only on an existing initialized store; not the strictest path |
| `profile-data` | Structured records | Appends `dataset_profile` event | No |
| `analyze` | Structured records | Appends `analysis` event | No |
| `join` | Structured records | Appends `source_join` event | No |
| `init` | Configuration/path | Creates directories/schema/database | No |
| `fetch`, `connector`, `refresh-rules`, `ingest` | Network/local originals | Creates source files/rows and provenance | No |
| `case create`, `case export` | Case/evidence | Creates case/export files and events | No |

This matrix describes this implementation; check current source before relying on an unfamiliar or changed command. General terminal/browser tools are not constrained by this table, and a skill is not a sandbox.

## Upgraded CLI routes

- `fraudlab inspect status|sources|verify|records ID` uses an existing SQLite connection opened with `mode=ro` and `query_only`; it does not initialize a missing home or append events. This is the preferred CLI route for strict evidence-store read-only work.
- `fraudlab bulk query`, `bulk join` and `bulk verify` verify raw/Parquet hashes without modifying the evidence store. DuckDB runs in memory with a private scratch spill directory, fixed memory/time budgets, no arbitrary user SQL and no automatic network/extension loading. Read-only describes the evidence store, not an assertion of zero scratch/runtime activity.
- `bulk acquire`, `bulk ingest`, `bulk convert` and `bulk connector` create immutable originals/dataset receipts and retain success/failure attempt records under `HOME/bulk`. They do not import all rows into legacy case SQLite.
- `web-search` calls the existing local SearXNG service. `web-extract` preserves original public .gov HTTP bytes plus separately hashed Crawl4AI response/rendered text under `HOME/web-acquisitions`. Extraction is an evidence-store write, not a read-only command.
- Native `research-local` extraction uses the same project acquisition implementation and also writes those transformation receipts. It does not bypass explicit HTTP access denial, authenticate, crawl links or use CAPTCHA services. Browser subresource egress is not a hardened network sandbox.

## Strict read-only route

For an explicit read-only review, do not call the event-writing analysis commands and do not initialize another store. Use the retained original files with standard-library readers, or open the existing SQLite database with `mode=ro`. Use `PRAGMA query_only=ON` as a second connection-local guard. Compute aggregates in memory and return them in the answer; do not persist new cases or analytical receipts unless separately authorized.

```python
import json
import sqlite3
from pathlib import Path

from fraudlab.settings import data_home
path = (data_home() / 'evidence.sqlite3').resolve()
with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
    db.execute('PRAGMA query_only=ON')
    for row in db.execute('SELECT id,label,records,extraction_status FROM sources'):
        print(row)
    # Parameterize a real returned source ID; do not invent one.
    # rows = db.execute('SELECT ordinal,data FROM records WHERE source_id=?', (source_id,))
    # Parse row JSON and count/group in memory without INSERT/UPDATE/DDL.
```

Use an already installed interpreter (`python -B` or the project's existing `.venv/bin/python -B`) rather than invoking environment synchronization or installation for a read-only question. Reading profile/session state may still cause the normal Hermes runtime to persist its own session; the guarantee here concerns the research evidence/case store, not every byte on the host.

## If an accidental write occurs

Disclose exactly which command ran, which event/file changed, and what did not change. Preserve the event rather than deleting evidence of the mistake. Do not call the original exercise a clean read-only pass. Record a failed boundary check, repair the missing procedural rule, and rerun a focused fresh-session exercise while independently comparing database contents and relevant file hashes before/after.
