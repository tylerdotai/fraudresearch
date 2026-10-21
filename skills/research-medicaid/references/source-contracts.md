# Medicaid release contracts

Reinspect each current release. Official discovery entry points: https://opendata.hhs.gov/datasets/medicaid-provider-spending/ , https://opendata.hhs.gov/datasets/medicaid-provider-spending-ndc/ , https://opendata.hhs.gov/datasets/medicaid-provider-enrollment-segments/ . These are discovery URLs, not bundled datasets or implemented Medicaid bulk connectors.

## Minimum recorded contract

Record publisher, requested/final URL, source ID, original hash and retrieval date; release/publication and observation dates; provider roles; identifier namespaces and validation; grain; geography; fee-for-service/managed care/CHIP scope; suppression; placeholder/blank handling; adjustments and denial semantics; amount units; revision status; exact required headers; actual rows and rejected rows; byte/time/memory/row budgets; rights/access constraints; and unsupported inferences.

## HCPCS release

A release may aggregate billing NPI × servicing NPI × HCPCS × month; verify its exact period and preliminary status. The month uses a service-line end/start anchor, not necessarily payment date. Both at least 12 claim lines and 12 beneficiaries are needed for a released cell. A claim can contain several lines; the count is not visits, time units or distinct claims. Blank roles can remain in source data. Paid fields reflect submitted line amounts, not a verified complete national expenditure measure. Read the actual current construction logic rather than assuming the file's name establishes semantics.

## NDC release

Confirm whether the NDC release uses billing and prescribing NPIs, not servicing NPI. Preserve NDC strings with leading zeros; validate format/product meaning separately and quarantine repeated-digit fills. The publisher warns that placeholder codes dominate unfiltered dollar sums and denied claims can contribute. Do not silently discard those rows and then present the remainder as all spending. Record excluded categories and reasons, and never add HCPCS and NDC totals without proving non-overlap.

## Enrollment projection

An enrollment projection can have enrollment segments by provider-state, but omits the underlying provider-state key and chooses one current NPI deterministically. Some ten-character values are placeholders or not numeric; dates can be sentinel values. Visible columns do not guarantee unique provider-state identity or a historically valid NPI crosswalk. Missing public segments cannot establish that a provider was unenrolled. A spend-versus-enrollment anti-join requires additional temporal/state identity evidence.

## Quality and privacy

Read CMS DQ Atlas/state-specific warnings before comparisons: https://www.medicaid.gov/dq-atlas/welcome . This is a discovery entry point, not an assertion that its current contents have been acquired. State agencies remain authoritative for their submissions. Released cells are a privacy-filtered subset, not a census; do not infer suppressed patient identities or seek raw beneficiary records. No public clinical eligibility or service-delivery evidence is implied by a payment aggregate.
