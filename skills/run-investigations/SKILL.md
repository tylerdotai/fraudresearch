---
name: run-investigations
description: "Use when planning national fraud investigations."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [check-program-fit, discover-national-sources, challenge-findings, prepare-case-files]
---

# Run Investigations

## Purpose and boundary

Run a falsifiable, bounded investigation. The deliverable is a reproducible evidence package or a supported decision to stop—not a list of suspicious organizations. No ongoing scan, filing, contact or publication is authorized by this skill.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before selecting a hypothesis: [Campaign design and observability](references/campaign-design.md).
- At every transition or interruption: [Stage gates and recovery](references/stage-gates.md).
- Before creating the campaign record: [Campaign brief](templates/campaign-brief.md).

## Procedure

1. Read the project README and your campaign checkpoint, if one exists. Run `fraudlab status` and `fraudlab verify` through the project environment. Record snapshot IDs, coverage and available connectors; do not re-download unchanged evidence just to appear active.
2. Load campaign-design before choosing targets. Write the hypothesis, observable contradiction, population, period, missing evidence, resource cap and stopping rule using the campaign template. National scope is not permission to call a bounded API sample a census.
3. Load check-program-fit and the domain skill. Complete a source contract before analysis. If the available data cannot observe the alleged conduct, change the question or stop; do not replace the missing signal with names, addresses or rankings.
4. Follow the stage-gate reference. Invoke preserve-evidence for acquisition, resolve-entities for joins, trace-federal-funds for program linkage and analyze-payments for quantities. Save commands and source versions alongside conclusions.
5. Invoke challenge-findings and review-originality before case preparation. A rejected hypothesis remains a useful result. Escalate material contradictions immediately; stage order never embargoes important findings.
6. Export a private draft or structurally complete case through prepare-case-files. Report what is established, what is not, and the next decisive fact. Obtain exact new approval for any external action.

## Completion contract

The campaign file contains its question, source/period coverage, executed steps, claim-to-evidence map, competing explanations, originality status and stop/continue decision. Every material finding has a source locator or an explicit unresolved label. A private artifact is delivered; no submission is implied.
