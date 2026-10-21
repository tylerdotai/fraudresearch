# FraudResearch contributor rules

Use Python 3.11+ and uv with the project environment. Read README.md and .env.example first.
Specify changed behavior with subprocess end-to-end acceptance before implementation.
Do not write after-the-fact unit tests. Use synthetic scratch stores, not real case data.
Run Ruff, mypy, both deterministic regression harnesses, skill validation and release acceptance.
Keep durable JSON test receipts under ignored artifacts/. Never publish those raw receipts.
The release-files.json allowlist defines distributable source. Update it deliberately.
Never add credentials, personal information, evidence, subjects or investigation history.
Do not infer wrongdoing from names, addresses, registry inclusion or statistical outliers.
No automatic submissions, contact, publication, paid access or scheduled research.
Review source semantics and contradictions; a green structural check is not a fraud finding.
