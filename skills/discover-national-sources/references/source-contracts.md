# Source contracts

## Minimum contract

Record these fields in the campaign, not as unsupported defaults:

```json
{
  "source_url": "exact requested URL",
  "publisher": "verified original publisher",
  "status": "discovered",
  "record_grain": "what one row represents",
  "identifiers": [{"field": "exact header", "namespace": "CCN/NPI/award/etc", "type": "string"}],
  "period": {"service": "unknown", "payment": "unknown", "publication": "source-stated", "retrieval": "actual timestamp"},
  "geography": "actual coverage, not presumed national",
  "access": "public/keyed/restricted",
  "rights": "source-stated terms or unresolved",
  "expected_columns": [],
  "pagination": "observed limits and completeness method",
  "suppression_missingness": "documented or unknown",
  "source_id": "after successful import",
  "analytical_uses": [],
  "unsupported_inferences": []
}
```

## State ladder

`discovered` = locator found. `reachable` = correct resource retrieved, not a login shell. `schema-verified` = required fields/types and record grain inspected. `exercised` = bounded repeatable import plus useful checks saved. `unavailable` = a documented failure, not proof the underlying records do not exist. `conditional` = access/approval/dependency unresolved. A catalog may be exercised while its data distribution fails.

## Coverage checks

Verify rows versus unique entities; snapshots versus transactions; fiscal versus calendar/service years; revisions; zeros versus suppression; geography and program coverage. A report total is a hard assertion: reconcile extracted/deduplicated counts programmatically and retain failures. Never conflate a returned page length with all results.

CMS catalog accessLevel public establishes public access metadata, not a blanket licence for every linked asset. Record actual terms. Do not promise redistribution rights based only on a .gov hostname. Mirrors share upstream lineage and do not create independent corroboration.

## Dynamic catalogs and aggregated claim releases

Prefer the live publisher resource metadata and rendered release page over search-index snippets when selecting a version; search results can lag a quarterly update. Preserve both the original HTTP response and any browser-rendered DOM, labeling the DOM as a transformation rather than original response bytes.

Treat reachable documentation, an offered download, a working schema tab and a schema-checked bulk import as separate acceptance states. Inspect the returned content after a tab click; a filename or click success cannot establish that schema content appeared. Retain failed-attempt captures with an explicit failed status rather than promoting them.

Read aggregation pseudocode and quality warnings before designing joins or ranking spending. Confirm provider roles, whether the date is a service anchor or payment date, suppression, denial/reversal handling, placeholder product codes and any omitted state/provider keys. A current identifier projected onto historical segments may not be a historical crosswalk. Missing public rows do not prove absence or ineligibility.

For public CSV archives that fail UTF-8 decoding, preserve original bytes and the failure. A reversible single-byte mapping can support structural inspection of ASCII headers/dates, but does not establish the publisher's encoding or authorize normalized entity-name matching. Record the decoding boundary explicitly.

## Negative evidence

A failed API lookup, inaccessible attachment or missing search hit supports only the bounded failure. Inspect official indexes, separately published public packets or verified alternate versions where appropriate. Keep exact original and actual retrieval URLs. Do not normalize a malformed source identifier into a different one and call it verified.
