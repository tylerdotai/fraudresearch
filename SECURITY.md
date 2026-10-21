# Security policy

This project is an early-stage research toolkit, not a forensic product, confidential intake system or security sandbox. Do not send fraud allegations or identifying evidence here.

For a software vulnerability, use GitHub's private vulnerability reporting feature if available on this repository. Do not open a public issue containing exploit secrets, credentials, private paths or real research data. If private reporting is unavailable, wait for a private channel rather than publishing sensitive details.

Supported release: 0.1.x on a best-effort basis. No guaranteed response time or independent security audit is claimed.

## Important boundaries

- General Hermes tools can do more than the persona permits. Human approvals and host isolation remain necessary.
- Official-host/DNS checks do not provide hardened browser egress isolation or defeat DNS rebinding.
- Local checksums are not tamper-proof storage, encryption or legal chain-of-custody certification.
- Model context, service logs and public-record identifiers need independent privacy review.
- Dependency installation executes package build/install logic; review pinned dependencies in your own environment.
- Never execute acquired source documents or bypass denied access.
