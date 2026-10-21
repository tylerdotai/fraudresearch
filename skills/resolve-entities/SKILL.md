---
name: resolve-entities
description: "Use when resolving provider or recipient identities."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [research-healthcare, trace-federal-funds, preserve-evidence]
---

# Resolve Entities

## Purpose and boundary

Resolve identity and relationships without turning string similarity into factual ownership or misconduct. Exact-value matches are necessary evidence in some joins but do not by themselves prove semantic identity.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before joins or identifier lookups: [Identifier contracts](references/identifier-contracts.md).
- Before candidate promotion or ownership assertions: [Matching workflow and link ledger](references/matching-and-link-ledger.md).

## Procedure

1. Load identifier-contracts. Preserve raw identifiers/names, establish their namespace, row grain and effective dates, and inspect missing/duplicate IDs before matching.
2. Write the intended relationship and expected cardinality. Separate same entity, same site, parent/subsidiary, branch, officer, beneficial owner, registered agent and shared address.
3. Load matching-and-link-ledger. Run explicit-key joins only after confirming the columns share identifier semantics. Use fuzzy matches for candidates; verify them with original independent records before promotion.
4. Inspect conflicts, duplicate keys, address purpose and temporal mismatches. Do not silently normalize a malformed source token or drop an inconvenient unmatched row.
5. Save a link ledger with source locators, confidence basis, contrary evidence and the precise relationship. Route unsupported links back to discovery; they may not become case facts.

## Completion contract

A reproducible linkage record distinguishes raw values, candidate matches and independently supported dated relationships. All material unmatched/conflicting records are retained. No ownership, fraud or personal identity is inferred from a fuzzy score, registered agent or shared address alone.
