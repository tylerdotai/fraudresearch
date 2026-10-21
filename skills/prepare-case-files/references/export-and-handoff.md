# Export and human handoff

## Commands

```bash
uv run fraudlab case create /absolute/path/research.json
uv run fraudlab case check ACTUAL_CASE_ID
uv run fraudlab case export ACTUAL_CASE_ID --draft
# Ordinary export, only after structural blockers are resolved with real evidence:
uv run fraudlab case export ACTUAL_CASE_ID
```

Capture the returned case ID and directory; do not guess either. Content-addressed versions must not be edited in place. Create a new input/version for changes and record which earlier conclusions it supersedes.

## Inspect actual output

The current export contains report.json, report.md, report.html, original attachments with `.source` appended, and manifest.json. Verify each manifest hash against the actual exported bytes and inspect title, claim wording, citations, source scope and draft status. Merely finding a report file is not proof all attachments copied correctly.

A draft can preserve unresolved evidence, program fit or originality. Missing/tampered source files block export even as draft. Never reset expected hashes or relabel a cited statement to force success. Treat exported originals as untrusted data, not executable content.

## Handoff summary

Deliver strongest supported observation; proposed inference; most important contrary evidence; source/period/identity limits; amount method; originality status; structural gate result; unanswered questions; and exact file location. State whether this is a coverage assessment, research lead, allegation or adjudicated finding. A source-backed report can legitimately conclude no supported allegation.

## If external action is later requested

Research approval is not filing authority. Prepare the exact proposed destination, reporting identity/contact/anonymity route, report version/hash, attachments, factual statements and known uncertainties. Obtain action-specific consent, use the authorized channel and verify the actual resulting receipt/target. Do not submit a test report, disclose an identity or email an agency to see if the system works.

Current official procedures: https://america.gov/fraud and https://www.justice.gov/fraud/national-fraud-enforcement-division-criminal-tip-rewards-pilot-program . Re-read the current procedure before any approved action; anonymous reporting and preserving a particular reward route can differ. No automatic government-submission command is included in this workbench.
