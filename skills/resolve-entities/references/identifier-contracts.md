# Identifier contracts

| Identifier | Typical role | Required caution |
|---|---|---|
| NPI | Provider enumeration | Ten-digit string format is not proof of issuance, licensure or certification |
| CCN | CMS provider certification namespace | Preserve leading characters/zeros; not interchangeable with NPI |
| EIN | Tax entity identifier | Do not repair/reformat an invalid raw token and claim original validity |
| UEI | Federal entity registration/award context | Different from tax IDs; verify current official format/source |
| License/site ID | Jurisdiction/program-specific | Namespace may repeat across states, programmes or sites |
| Award/transaction ID | Funding record | Award identity and action identity may differ |

Store `(namespace, raw_value, source_id, locator, effective_date)` before deriving comparison keys. If normalized search variants help discovery, keep them separate from original values and record the transformation. Never let successful fuzzy lookup validate a malformed original identifier.

## Grain and cardinality

Determine one row per organization/site/license/measure/period/transaction before deduplication. Duplicate ID values can be legitimate across branches, periods or measures. One organization may have multiple site or certification relationships; do not infer a one-to-one NPI–CCN crosswalk. A shared controlling entity needs dated source evidence, not a count of names at an address.

## Temporal identity

Record mergers, name changes, DBA dates, transfers, ownership effective dates and source update times. A current relationship cannot automatically establish who controlled an entity during an older payment period. Disagreement between authoritative records can indicate different dates or purposes, not necessarily deception.

## Address purposes

NPPES explicitly distinguishes mailing and practice locations; inspect labels and returned objects. A mailing suite, registered-agent address, virtual office, hospital campus or landlord can create a cluster without common beneficial ownership. Preserve unit numbers and source spelling; do not strip them before testing a shared-site assertion.
