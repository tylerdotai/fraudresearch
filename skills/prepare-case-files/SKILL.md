---
name: prepare-case-files
description: "Use when packaging private fraud-research cases."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [preserve-evidence, check-program-fit, review-originality, challenge-findings]
---

# Prepare Case Files

## Purpose and boundary

Convert research into a checkable private record. Case completeness is structural evidence organization, not proof of crime, legal eligibility or permission to file. Do not pad missing facts to clear the export gate.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before creating JSON or interpreting a check: [Case schema and gate semantics](references/case-schema.md).
- Before export or a human handoff: [Versioned export and approval boundaries](references/export-and-handoff.md).
- For an incomplete starting scaffold: [Case input template](templates/case-input.json).

## Procedure

1. Load case-schema and the project docs/CASE-FORMAT.md. Create a claim ledger first: each fact/inference, classification, source ID, locator, exact quote, interpretation and contrary evidence. Use the input template as an incomplete scaffold, never as a discovered case.
2. Complete program fit, federal/health-care basis as applicable, originality review, amount methodology, alternative explanations and limitations. Where the tool schema is narrower than substantive rules, explain the mismatch; do not fabricate a funding citation to satisfy a field.
3. Run case create/check through the actual workbench. Inspect every blocker and resolve it with evidence or keep a draft. The checker verifies quotation presence, not whether its interpretation establishes funding, guilt or originality.
4. Load export-and-handoff. Export with --draft when incomplete, verify copied originals/manifest and inspect the rendered report. Preserve version IDs and changed-source dependencies; never edit content-addressed case files in place.
5. Deliver the private package and review note. No filing command exists. Any later submission/contact/publication needs exact destination, identity, content and attachments approved separately, followed by actual receipt readback.

## Completion contract

The delivered private package has truthful classifications, verified source locators, reproducible quantities, originality/fit limitations, contrary evidence and a checked attachment manifest. Draft blockers remain visible. Export success is never described as submission, award approval or a fraud determination.
