# Calculation contracts

## Input contract

Record exact source ID/hash, field names, unit/currency/scale, meaning (paid/claimed/budget/obligation/relative measure), sign convention, row grain, service/payment/accounting dates, cohort selection, denominator source, missing/suppression handling, duplicates, corrections and exchange/rounding method if relevant.

Do not analyze a field as money because its label contains spending. Home-health releases can include comparison measures rather than direct dollar payment columns. Agency budget resources and recipient losses also differ.

## Existing executable scope

```bash
uv run fraudlab profile-data SOURCE_ID --group 'State'
uv run fraudlab analyze SOURCE_ID --group 'exact group column' --amount 'exact monetary column'
```

The first counts published rows by value. The second sums Decimal-converted amounts by group and rejects missing/non-finite/invalid values. Neither command validates the economic meaning of a column, implements risk adjustment, estimates causal effects or outputs a fraud probability. A formatted dollar string, thousands separator or suppression symbol may fail parsing; inspect and document an authorized derived transformation rather than silently stripping content.

`records` exposes a bounded view; it is not all rows for a large source. Use documented source counts, grouping output or explicit reproducible analysis of the preserved original. Do not calculate from only the first displayed page and label it a full-source total.

## Join contract

Record intended one-to-one/one-to-many grain before combining tables. A many-to-many join can multiply amounts. Count matched/unmatched/duplicate keys and compare pre/post totals. An exact string match does not validate identifier semantics. Retain raw IDs and source versions.

## Derived output receipt

- Question and formula, with units.
- Source IDs/hashes, columns and filters.
- Included/excluded/unparsed counts and reasons.
- Date/cohort/denominator comparability.
- Executed command/script version and output.
- Reconciliation/sensitivity checks.
- Interpretation supported and stronger claims not supported.

This receipt is a research sidecar; the case CLI does not enforce all these analytical requirements. Do not confuse a valid JSON case with a valid calculation.
