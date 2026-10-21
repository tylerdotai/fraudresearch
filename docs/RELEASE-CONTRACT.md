# Public-release acceptance contract

This contract and `tests/release_e2e.py` precede release-specific implementation.
The regression harnesses cover the existing workbench; this suite exercises its public boundaries.

## Known failure modes

1. The default evidence store is inside the checkout or installed package.
2. A fresh shell lacks the developer's scratch setting.
3. Search or rendering silently reuses a developer endpoint or remote fallback.
4. Settings accept non-loopback or credential-bearing services.
5. Invalid JSON settings produce an unclear crash.
6. Evidence, sessions, credentials or unexpected files enter a release.
7. Personal paths, internal network addresses or private-key material enter approved text files.
8. A checksum is missing, stale or bypassed by modified file content.
9. A symlink imports material outside the release.
10. Skill references depend on private paths or missing packages.
11. The offline demonstration implies a real case, submission or adjudication.
12. An extracted release works only because the developer checkout is on the import path.
13. Hermes installation writes into a real existing profile instead of an isolated test home.
14. Git commit metadata exposes a personal author name or email.
15. The public Git tree differs from the payload reviewed locally.
16. Generated mascot graphics carry hidden EXIF, XMP or other metadata. Only the four reviewed, explicitly named WebP assets are permitted as raster content; metadata injection must be rejected independently of checksums.

## Acceptance

- Run the subprocess suite in an empty home without inherited service settings or TMPDIR.
- Use synthetic data only; preserve JSON receipts outside the distribution payload.
- Exercise the real CLI, private scratch, exact query and draft export.
- Inject each privacy failure independently and require release rejection.
- Build a ZIP from the explicit file list, extract it, verify every SHA256 and scan its contents.
- Validate all 13 skills and their relative links.
- Install the distribution using an isolated Hermes home; inspect copied files and run the installed plugin.
- Run Ruff, mypy and both deterministic regression harnesses.
- Publish only enumerated reviewed files with a generic commit identity.
- Read the public repository back and compare commit/tree/file metadata before claiming publication.

These checks are structural and privacy controls, not proof of a criminal offense or a guarantee that all sensitive information can be detected automatically. Source review and an allowlist remain mandatory.
