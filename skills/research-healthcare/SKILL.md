---
name: research-healthcare
description: "Use when investigating hospice or home health."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [discover-national-sources, resolve-entities, analyze-payments, challenge-findings]
---

# Research Healthcare

## Purpose and boundary

Investigate healthcare mechanisms using source-specific methods. Registry enrollment, Medicare certification, ownership categories, quality measures and claims are not interchangeable. Public provider files cannot establish individual false visits or clinical eligibility.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before acquisition, joins or interpreting fields: [Healthcare dataset contracts](references/dataset-contracts.md).
- Before selecting a fraud mechanism or interpreting an outlier: [Mechanism tests and alternative explanations](references/hypothesis-tests.md).

## Procedure

1. Load dataset-contracts before querying. Define the alleged mechanism and the exact records needed to observe it. Classify the available source as registry, certification, ownership, quality, utilization, payments or enforcement—not simply healthcare data.
2. Run the appropriate implemented connector and inspect actual headers, source dates, row counts, footnotes and certification identifiers. Use the published snapshot population, not a presumption that all agencies/patients are represented.
3. Load hypothesis-tests before interpreting an anomaly. Write a mechanism-to-evidence card including the strongest benign explanation and decisive missing record. Stop a patient-level hypothesis if only provider-level data exists.
4. Load resolve-entities before combining CCNs, NPIs or corporate records. Keep organizational branches, effective dates, address purposes and ownership categories distinct. An authorized official is not automatically a beneficial owner.
5. Analyze matched periods/cohorts and preserve denominators, exclusions, suppression and contrary evidence. Verify derived quantities with tools. An unusually high ratio, shared address or long survival is not self-proving misconduct.
6. Produce a healthcare findings matrix with observed facts, inferred links, unavailable records and falsification results. Pass it to challenge-findings and review-originality, not directly to a public allegation.

## Completion contract

The report identifies the exact source population/period and the evidence needed for each proposed mechanism. Every identity or financial link has a locator or remains unverified. No patient-level conduct is inferred from provider aggregates, registry status or quality ratios.
