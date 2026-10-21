# Verification

## Local release checks

Verified on Linux with Python 3.14.7, uv 0.11.3 and Bun 1.3.14:

| Check | Observed result |
|---|---|
| Ruff and mypy | Passed; nine workbench source modules type-checked |
| Original deterministic CLI contracts | Passed; 44 subprocess commands |
| Bulk and strict-read-only contracts | Passed; 49 subprocess commands |
| Release and privacy contracts | Passed; 30 subprocess commands, including mascot, logo, social-card and README-banner metadata rejection |
| Research skill graph | Passed; 13 skills and six executable help contracts |
| Live web and source connectors | Passed in separate scratch stores; five bulk connectors |
| Isolated installed Hermes profile | Passed fresh six-command offline install/provider/demo run; earlier seven-command live run also exercised native search/extract; no model calls |
| Production website | Passed; 28 desktop/mobile browser contracts including axe, clipboard, navigation, artwork, government-context figures, canonical/crawler consistency, reduced motion, optical alignment, uncropped illustrations and real HTTP 404 recovery with JavaScript disabled |

These are software acceptance results, not an independent security audit, legal review, clinical assessment or finding of fraud. Raw local receipts are not published because they can contain local paths and acquired records. GitHub Actions independently repeats the deterministic and production-website checks; consult its actual run status rather than treating this table as a future guarantee.

## Repeatable deterministic acceptance

Run the six commands in README. JSON receipts are retained locally under ignored artifacts/; they can contain local paths and are not public release material.

The release-specific contract and subprocess test were specified before the portability/privacy implementation. It checks empty-home operation, external data storage, missing/rejected service settings, scratch without TMPDIR, synthetic bulk operations and draft demo, independent privacy injections, manifest tampering, symlinks and execution from an extracted release.

The original deterministic harnesses cover ingestion, duplicate source handling, Decimal sums, exact-value joins, source tampering, quote locators, case gating, malformed CSV/ZIP, string preservation and bounded query behavior. These are software checks, not forensic or legal certification.

## Optional live acceptance

With your own loopback service configuration and explicit network access:

```bash
uv run python tests/upgrade_e2e.py web
uv run python tests/upgrade_e2e.py connectors
```

These contact actual sources and can fail on schema, service or network drift. Connector acceptance downloads identifying public records to scratch stores; never publish the resulting receipts or data. No live source scans are scheduled by CI.

## Hermes install acceptance

Use a disposable isolated Hermes home, not another real profile, to install the local distribution. Verify expected skills/config/source files and exercise the actual provider through the installed runtime. A metadata/link check alone is not proof a model-backed investigation works. Initial verification does not claim platform coverage beyond the recorded environment.

```bash
uv run python tests/hermes_e2e.py --hermes-source /path/to/installed/hermes-agent
```

This installs from an extracted clean candidate, verifies the home boundary before installation, syncs an isolated workbench, validates skills through the native Hermes runtime and checks fail-closed provider behavior without model calls. It also runs the installed synthetic demo. It does not modify a real profile or install dependencies into Hermes.
