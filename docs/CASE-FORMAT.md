# Private case format

Create a JSON object with the following fields. Replace descriptions with source-supported material; do not copy the examples as findings. The agent supplies interpretation; tools validate structure, source integrity and quotation presence, not legal truth.

```json
{
  "title": "Specific research question, entity and period",
  "sector": "hospice",
  "claims": [
    {
      "text": "A narrowly stated observation supported at this locator",
      "classification": "fact",
      "source_id": "actual source ID returned by import",
      "locator": "row:1",
      "quote": "Exact text present in that row"
    }
  ],
  "federal_nexus": {
    "status": "unverified",
    "explanation": "What is documented and what remains missing"
  },
  "originality": {
    "status": "unverified",
    "explanation": "What the independent analysis adds, or why novelty is not established"
  },
  "alternative_explanations": ["A concrete innocent explanation to investigate"],
  "unanswered_questions": ["The next decisive missing fact"]
}
```

For a documented federal nexus, add `source_id`, `locator`, and `quote` to that object, set `status` to `documented` and explain why the cited evidence establishes the relevant funding/program link. Do not label the general existence of an agency as evidence of a particular recipient's federal funding.

Originality status `independent_analysis` requires an explanation of the genuinely new, reproducible analysis. `restatement` and `unverified` block ordinary export. The tool checks the declaration's presence, not its substantive correctness or government knowledge.

Classifications: `fact`, `anomaly`, `allegation`, `adjudicated`. An adjudicated classification requires actual authoritative support; a tool accepts the label but cannot decide whether it is deserved.

Sectors: hospice, home-health, day-care, special-services, agriculture, labor, housing, education, veterans, small-business, healthcare, other-review-required. These are research categories, not an exhaustive legal eligibility map; the last category blocks ordinary export.

Locators: `row:N` for structured records, `page:N` for PDF text, `line:N` for extracted text. Quotes must be present in that specific locator. Exact quote presence does not prove the claim's interpretation. Sources and extracted text must pass checksum checks. Incomplete or uncited work can be exported only with `--draft`, and missing/tampered source material cannot be exported even as draft.

Each create produces a content-addressed version. Editing an existing case file in place breaks its ID/hash check; create a new version instead. Exports include raw attachments with `.source` appended to discourage accidental execution, a private HTML view, JSON, Markdown and a checksum manifest. No export constitutes a government submission or approval to submit.
