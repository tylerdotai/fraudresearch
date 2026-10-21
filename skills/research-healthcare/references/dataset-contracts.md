# Healthcare dataset contracts

## Verified working sources

| Source | Unit and useful fields | What it does not establish |
|---|---|---|
| CMS Hospice General Information | Published provider row; `CMS Certification Number (CCN)`, `Facility Name`, `State`, `Ownership Type`, `Certification Date` | Claims, actual visits, beneficiaries, complete corporate ownership |
| CMS Home Health Care Agencies | Published agency row; CCN, `Provider Name`, `Type of Ownership`, service flags, quality measures/footnotes | Paid invoices, patient eligibility or all providers in all programs |
| NPPES 2.1 Type-2 query | Organization NPI; `basic.organization_name`, `addresses`, `taxonomies`, dates, authorized-official fields | Licensure/credentialing, Medicare certification, claims or beneficial ownership |

The headers above are illustrative source contracts. Validate the current release before relying on them. CMS discovers distributions from https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items ; current topic pages are https://data.cms.gov/provider-data/dataset/yc9t-dgbk and https://data.cms.gov/provider-data/dataset/6jpm-sxkc . Do not hardcode a dated CSV download URL into an investigation.

## Critical home-health field distinction

The exercised home-health CSV includes `How much Medicare spends on an episode of care at this agency, compared to Medicare spending across all agencies nationally` and an episode-count field. Its label describes a relative comparison, not a dollar total. Do not sum it as money or multiply it into a loss without its actual methodology. Numerator/denominator/footnote fields belong to specific measures; one measure's denominator cannot be borrowed for another. Read the source dictionary/methodology for the relevant release before clinical/statistical interpretation.

## Bounded schema inspection

Do not dump the full provider CSV or thousands of rows into model context. Read exact headers first, then compute only the required aggregates in memory. During strict read-only work use an existing interpreter with `-B`, not event-writing workbench analysis commands. Obtain the path from retained source metadata, not a guessed filename.

```python
import csv
from pathlib import Path

# source_path is the exact retained original path from source metadata.
with Path(source_path).open(newline='', encoding='utf-8-sig') as handle:
    rows = csv.DictReader(handle)
    print(rows.fieldnames)  # Schema only; no provider-row dump.
```

If testing identifier completeness, emit only row/missing/unique/duplicate counts plus source ID and counting unit. A repeated CCN is a record-grain question before it is an entity or payment claim. Preserve unmatched detail on disk only when writing is authorized.

## NPPES contract

Official documentation: https://npiregistry.cms.hhs.gov/api-page . It explicitly warns that issuance of an NPI does not ensure or validate licensure or credentialing. Version 2.1 is documented; limit 1–200, skip up to 1000, and organizational type alone is not a sufficient query. The API is not an unrestricted national enumeration mechanism.

Use the `address_purpose` label and the actual returned object when distinguishing mailing and practice locations. Multiple practice locations, other names and identifiers may exist. Search results may match a former/DBA name rather than the displayed legal business name. Inspect the returned evidence rather than declaring a mismatch or common owner.

## Missing layers

CMS ownership/enrollment datasets, utilization/payment files, exclusion lists and court/enforcement records must each be evaluated separately; this profile does not automatically implement all of them. A quality dataset is not a claims table. An exclusion-name candidate is not a confirmed match. Published public aggregates do not permit reconstruction of private patient identities.

Before a join, record namespace, raw ID string, record grain, effective dates, source version and expected cardinality. CCN and NPI may have different relationships; do not invent a one-to-one crosswalk. Certification dates and registry update/certification fields have source-specific meanings.
