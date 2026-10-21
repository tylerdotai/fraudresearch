# Case schema and gate semantics

The installed CLI's authoritative local guide is docs/CASE-FORMAT.md in the workbench. Recheck `fraudlab case --help` when the runtime changes. Do not invent flags or fields the checker is claimed to enforce.

## Required research fields

- `title`: nonempty, specific neutral question/entity/period.
- `sector`: supported research category; `other-review-required` intentionally blocks ordinary export. Categories are not a complete legal scope definition.
- `claims`: classified statements with `text`, `classification`, `source_id`, `locator`, `quote`.
- `federal_nexus`: declared status/explanation and, when documented, its own source/locator/quote.
- `originality`: declared status/explanation; `independent_analysis` needs a genuine reproducible analytical delta, not just a label.
- `alternative_explanations`: concrete possibilities checked or unresolved.
- `unanswered_questions`: decisive limitations; do not erase unknowns to look complete.

Classifications: fact, anomaly, allegation, adjudicated. The tool accepts the classification but does not determine whether a judgment exists or a sentence is true. Cite the actual adjudication before using that label. A prosecutor's allegation and a court finding are different.

## Citation locators

`row:N` means one-based parsed record; `page:N` means PDF position; `line:N` means preserved extraction line. Exact quote presence can validate the wrong interpretation, particularly a bare amount, name or agency mention. Read context, row grain and source headers. Preserve extra analytical/contrary-evidence notes as sidecars; do not imply the CLI validates their substance.

## Current blockers

The checker covers integrity, supported sector, claims/classification/quote structure, documented-nexus citation, independent-analysis declaration, alternatives and limitations. A PASS is structural completeness only. It does not prove criminal intent, independent source credibility, actual federal payment linkage, novelty to authorities or tipster eligibility.

The current schema conservatively requires a documented `federal_nexus` for ordinary export, while program fit may require a more nuanced health-care subject-area assessment. Keep such work as a draft and state the schema limit rather than inventing evidence or incorrectly declaring the legal route excluded.

## Incomplete template

Use templates/case-input.json after replacing fields with actual research. Placeholders deliberately do not clear the gate. Keep synthetic examples and test fixtures in separate scratch stores. Do not create a production allegation merely to demonstrate a feature.
