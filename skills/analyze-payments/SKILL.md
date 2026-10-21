---
name: analyze-payments
description: "Use when reconciling payments and questioned amounts."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [resolve-entities, preserve-evidence, challenge-findings]
---

# Analyze Payments

## Purpose and boundary

Produce reproducible financial observations, not a fraud score. Distinguish money actually paid, accounting entries, claimed/authorized amounts, recoveries and adjudicated loss. A mathematically correct total can still answer the wrong question.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before any computation: [Calculation contracts and units](references/calculation-contracts.md).
- Before interpreting a total, variance or outlier: [Reconciliation and worked examples](references/reconciliation-and-examples.md).

## Procedure

1. Load calculation-contracts before running a comparison. Record source IDs/versions, units/currency, row grain, date basis, cohort, expected denominator, exclusion rules, duplicates, reversals and missing/suppressed values.
2. Verify sources and key cardinality through preserve-evidence and resolve-entities. Establish which inputs are money; relative spending/quality metrics may not be dollar amounts.
3. Execute the smallest appropriate calculation with tools. The installed analyze command provides grouped Decimal sums only; profile-data counts rows. Ratios, statistical tests and complex cohort work need a separately documented reproducible calculation, not invented CLI flags.
4. Load reconciliation-and-examples and reconcile inputs, joins, displayed totals and independent source records. Preserve unmatched rows and errors. Do not coerce missing/suppressed values to zero or count both sides of transfers as losses.
5. Save the calculation receipt, interpretation, sensitivity to assumptions and contrary evidence. Report observed amount, questioned amount and established loss separately. Route material findings to challenge-findings before writing stronger claims.

## Completion contract

Another reader can reproduce the result from pinned inputs and explicit formulas, including coverage and excluded rows. Unit/period/grain mismatches and unresolved reconciliation gaps are disclosed. No amount is called a loss merely because it is unusual or above budget.
