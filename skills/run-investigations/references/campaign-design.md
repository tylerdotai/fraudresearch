# Campaign design and observability

## Choose a question the sources can answer

Start with a mechanism, not a demographic, neighborhood or provider name. Write `If H were true, record X during period T would differ from an independently supported constraint Y; explanation Z could instead account for that difference.` This is a research hypothesis, not an accusation.

| Proposed question | Required observable | Public sources actually available | Decision |
|---|---|---|---|
| Does a published provider file contain duplicate certification IDs? | Identifier, source row, version, scope | CMS provider snapshot | Test record duplication; do not infer duplicate billing |
| Did a provider bill for visits never made? | Claims plus reliable evidence of service delivery | Provider registry/quality CSV only | Not observable from these files; do not claim fake visits |
| Does a recipient have a documented federal award? | Award ID, recipient ID, date, agency/program | Agency-reference list only | Insufficient; discover award-level evidence |
| Does a child-care payment exceed an applicable limit? | Correct unit/rate, eligibility period, paid units, adjustments | License capacity plus annual grant total | Insufficient without matched payment rules and units |

## Selection card

Record sector and exact program; mechanism; geographic population; record/service/payment dates; expected supporting record; strongest contrary record; entity identifiers; amount units; available versus missing data. Record why these sources, not why a person looks suspicious.

Select one primary hypothesis per bounded campaign. Secondary observations enter a lead ledger with provenance, not silent scope expansion. A national campaign can use a full published national snapshot; a targeted API query must identify its search boundaries and truncation.

## Resource and stopping rules

Use a finite number of sources, requests or investigation steps. Start with already imported official snapshots. No full NPPES crawl, unbounded download or paid-data purchase is implied. Define the stopping event before acquisition: falsifying record found; required evidence inaccessible; source coverage invalidates inference; approved resource cap reached; or enough evidence exists for private review.

Prioritize original analytical potential, strength of identifiers, observable conduct, public evidence access, coverage quality and disconfirmability. Do not optimize the target list for expected payout or use a fabricated fraud-probability score.

## Worked synthetic example — duplicate row versus conduct

A synthetic provider CSV repeats the same CCN and name in two rows. First inspect the row grain: branches, versions, measures or periods may legitimately repeat the ID. Group by the complete intended key before counting entities. A confirmed duplicate publication is a data-quality finding. It does not establish two payments, two patients or intent.

Output: question, required observation, actual source coverage, measurement plan, competing explanation, and next decisive record. If no public source can supply that record, end with a bounded limitation rather than escalating the language.
