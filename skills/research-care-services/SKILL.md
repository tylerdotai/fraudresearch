---
name: research-care-services
description: "Use when researching day care or special services."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [check-program-fit, trace-federal-funds, resolve-entities, challenge-findings]
---

# Research Care Services

## Purpose and boundary

Investigate care-service funding without inventing a national child-care payments database or equating licensing with subsidy receipt. Define special services from authoritative program documents; it is not a catch-all label the analyst may assign.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before selecting the program and sources: [Program and source map](references/program-and-source-map.md).
- Before doing capacity, service or payment comparisons: [Capacity/payment tests](references/capacity-and-payment-tests.md).

## Procedure

1. Load program-and-source-map. Identify the exact federal/state/tribal program, administrator, recipient/site, applicable period and allegation mechanism. Do not import a nearby locality as the campaign boundary.
2. Create a jurisdictional source contract: licensing authority and exemptions, provider/site IDs, public funding source, payment rules, rate unit, eligibility/attendance or enrollment basis and revision history. Discover actual sources before choosing a scoring method.
3. Load capacity-and-payment-tests before comparing license capacity, children served, slots, enrollment, attendance or money. Read the applicable plan/rules for the specific dates. Neither unused capacity nor a closed-day observation proves a false claim.
4. Trace the relevant funding/payment edge and distinguish legal entity, licensed site, subsidy recipient, grant recipient and contractor. Use exact identifiers and temporal evidence; private child/family records are outside this public-source workflow.
5. Report only supported, original observations, strongest contrary explanations and the missing decisive record. If source access is restricted or program meaning remains undefined, mark the branch blocked rather than producing a guessed conclusion.

## Completion contract

A program-specific dossier identifies the applicable rules, source coverage, units, recipient/site relationships and funding evidence. Any undefined special-services category or unavailable payment layer remains an explicit blocker. No patient/child records or unauthorized contacts are used.
