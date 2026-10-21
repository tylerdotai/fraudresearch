---
name: research-medicaid
description: "Use when analyzing Medicaid provider spending data."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, medicaid, evidence, public-records]
    related_skills: [discover-national-sources, preserve-evidence, resolve-entities, analyze-payments, challenge-findings, review-originality]
---

# Research Medicaid

## When to Use

Use for public Medicaid/CHIP provider-spending, enrollment, exclusion and credential timeline analysis. This skill does not authorize private beneficiary data or submissions.

## Purpose and boundary

Test a specific Medicaid/CHIP program-integrity hypothesis using dated source contracts and reproducible public-data transformations. National source remit is not complete claims coverage. Do not reconstruct patient identities, infer false diagnoses from code volumes, or label reported amounts as federal losses.

## Reference loading

- Before any CLI call: [Command effects](../preserve-evidence/references/command-effects.md).
- Before acquisition, filtering or sums: [Medicaid source contracts](references/source-contracts.md).
- Before exclusions, enrollment or licensing joins: [Temporal and provider-role tests](references/temporal-tests.md).
- Before using the upgraded CLI: [Bounded pipeline and handoff](references/pipeline.md).

## Procedure

1. State one falsifiable question, exact program, provider role, population, service/payment period, denominator and stop condition. A high total or registry inclusion is not a hypothesis of criminal conduct.
2. Read source-contracts and the release's actual documentation/pseudocode. Identify the meaning of every role, date, payment field, missing value and suppression rule. Do not import a field definition from another release or the similarly named NDC file.
3. Use the bounded pipeline only after byte, row, expansion, disk and time budgets are selected. Preserve original bytes and raw/member/Parquet hashes. A catalog, download, parsed schema and useful import are separate states; failed attempts remain in the provenance record.
4. Validate exact identifier strings before joining. Retain billing, servicing and prescribing roles separately. Read temporal-tests; use authoritative historical exclusion/reinstatement, enrollment or credential intervals. Blank, placeholder, invalid and unmatched values remain separate accounting categories.
5. Establish service location/program from independent records; an NPI mailing address is not the claim's submitting state. If a public projection omits the state/provider key or substitutes a current identifier for historical records, do not turn an unmatched row into an eligibility finding.
6. Record aggregation grain, revised-data status, suppression and denial/adjustment handling before calculating. Beneficiaries cannot be summed across overlapping cells as unique people. Claim lines are not visits, hours or billable units. Do not multiply the whole amount by a guessed federal match rate.
7. Challenge every surviving contradiction using corrections, exceptions, provider-role errors, date ambiguity, reinstatement and state data quality. Separate reported activity, confirmed paid amounts, questioned amounts and proven losses. A generic exact-value match proves neither identity nor wrongdoing.
8. Complete claim-by-claim prior-publication review. OIG work plans and earlier audits are known context, not original discoveries. Keep government prior knowledge and award eligibility unknown. Produce a private incomplete package with decisive missing evidence; no filing or contacts.

## Completion contract

The deliverable records actual source versions and coverage, input/member/output hashes, deterministic commands, raw counting units, validated identifiers/roles, date intervals, unmatched/suppressed/invalid categories, arithmetic with units, strongest benign explanations, prior-publication status and a stop/continue decision. Missing public rows are never described as proof of nonparticipation or zero spending. No patient records, automatic fraud scores, submissions or scheduled scans.
