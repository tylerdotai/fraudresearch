---
name: discover-national-sources
description: "Use when qualifying national public-data sources."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [preserve-evidence, research-healthcare, research-care-services]
---

# Discover National Sources

## Purpose and boundary

Find complementary original sources for the chosen observable question. A directory, catalog entry, readable page and exercised useful import are different evidence states. Do not install a flat list of OSINT tools or call a sampled API a complete national database.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before choosing a source: [Source contract and acceptance states](references/source-contracts.md).
- Before running acquisition: [Connector contracts and recovery](references/connector-runbook.md).

## Procedure

1. Load source-contracts and inspect SOURCE-REGISTRY.json. Identify which required evidence units are already available, candidate-only or unavailable. Prefer original agencies to mirrors.
2. Before acquisition, record publisher, access/rights constraints, record grain, identifiers, observation dates, geography, refresh cadence, limits, suppression and required columns. Reject a source that cannot answer the question even if it is easy to download.
3. Follow connector-runbook for implemented commands. Save the catalog and distribution lineage. Validate actual payload, headers and rows, not only HTTP 200. Check declared totals and pagination where provided.
4. Acquire within approved resource bounds and run preserve-evidence. Mark a connector exercised only after a useful schema-checked import; update its limitations as carefully as its success state.
5. For blocked/keyed/non-.gov sources, record the actual limit and propose the smallest authorized next step. Do not bypass restrictions, invent endpoint paths, silently switch source identity or label missing data as nonexistent.

## Completion contract

Each used dataset has an explicit source contract, preserved original and observed schema/coverage. Working versus conditional integrations are distinguished. Counts retain their unit; unmatched/unparsed material and retrieval gaps remain visible.
