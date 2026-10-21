---
name: challenge-findings
description: "Use when challenging suspected-fraud findings."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [analyze-payments, resolve-entities, review-originality, prepare-case-files]
---

# Challenge Findings

## Purpose and boundary

Challenge an inference against its strongest realistic alternative. The goal is not to defend the investigation or make every candidate survive; a well-supported rejection is a successful research outcome.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before assessing a pattern: [Falsification and contrary-evidence matrix](references/falsification-matrix.md).
- Before handing off or accepting a tool PASS: [Substantive release review](references/release-review.md).

## Procedure

1. Load falsification-matrix before evaluating the headline. Rewrite each material claim as an observation plus the additional inference being made. Name the decisive record that could overturn that inference.
2. Trace source lineage and test independent corroboration. Load release-review before any case handoff. Verify identity/time, units, completeness, amount grain, governing rules and the status of allegations versus judgments.
3. Search for benign explanations and contrary records with at least the same specificity used for supporting evidence. Do not quietly remove a contradictory source, widen a period or change a cohort to preserve the result.
4. Mark each claim supported, narrowed, contradicted or unresolved with exact locators and reasoning. Route arithmetic/identity/funding/originality gaps to the owning skill. Important findings are disclosed immediately, not delayed for a preferred narrative.
5. Produce a challenge report and action recommendation. Keep low-evidence cases private/draft or close them; a software PASS never overrides a failed substantive check.

## Completion contract

Every load-bearing inference has a tested plausible alternative, a source-backed disposition and a bounded uncertainty statement. Contradictory evidence remains in the package. No automatic positive verdict is produced merely because citations or file hashes pass.
