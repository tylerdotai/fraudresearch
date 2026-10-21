---
name: trace-federal-funds
description: "Use when tracing federal awards and reimbursements."
version: 2.0.0
author: FraudResearch contributors
license: MIT
metadata:
  hermes:
    tags: [fraud-research, evidence, public-records, national-programs]
    related_skills: [discover-national-sources, resolve-entities, check-program-fit]
---

# Trace Federal Funds

## Purpose and boundary

Establish a specific program/recipient/transaction funding chain. A federal agency reference or a state grant headline is not evidence that a questioned transaction used federal funds. Read the actual program scope before imposing or asserting a funding-nexus requirement.

## Reference loading

- Before any CLI call in read-only work, or when command effects are uncertain: [Command effects and strict read-only route](../preserve-evidence/references/command-effects.md).
- Before defining the required linkage: [Funding-chain methods](references/funding-chain.md).
- Before reading award/payment fields or proposing an API: [Award-data contracts and limits](references/award-data-contracts.md).

## Procedure

1. Load funding-chain before choosing sources. State the required connection: direct award, pass-through/subaward, loan, contract, benefit payment or reimbursement. Preserve program-specific alternatives and identify the missing edge.
2. Load award-data-contracts. Verify identifiers, recipient grain, transaction versus award totals, action/effective dates, period and amended/cancelled/recovered amounts before using dollar fields.
3. Use official recipient/award records or authorized public originals. The implemented agencies connector supplies only agency references; do not manufacture an awards API integration or treat agency budget totals as recipient payments.
4. Build a dated edge ledger linking each entity/program/award/payment with its source ID and locator. Resolve identity through resolve-entities and examine contradictions or unlinked pass-through steps.
5. Prepare the case federal_nexus object only when the specific asserted edge is supported. Otherwise keep unverified with the exact next record needed; do not relabel an agency citation to satisfy software gates.

## Completion contract

Every asserted funding edge has a specific identity, period and cited original record. Amounts retain their type and are not double-counted across award/action/recipient layers. Unresolved links block a documented-nexus claim even if the portal can accept a report.
