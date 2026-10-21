# Matching and link ledger

## Executable operations

```bash
uv run fraudlab match 'exact observed organization name'
uv run fraudlab join LEFT_SOURCE RIGHT_SOURCE --left-key 'exact header' --right-key 'exact header'
```

`match` returns similarity candidates, not confirmed identity; it scans a bounded number of stored rows and is not exhaustive. `join` compares raw column values after string conversion and returns at most 10,000 pairs with a truncation flag. It does not validate namespace, crosswalk semantics, date overlap or ownership. Inspect duplicates/cardinality before interpreting pairs.

## Candidate decision

1. Compare exact source IDs and stable identifiers with the same namespace.
2. Check names/DBAs and dated site information as corroboration, not replacement identifiers.
3. Determine the relationship actually supported; shared officer is not automatically common ownership.
4. Look for contradictions: distinct identifiers, addresses during the relevant date, incompatible legal entities, branches or source errors.
5. Retain candidate/unresolved status unless independent evidence supports the precise edge.

## Link record

```json
{
  "left": {"namespace": "source-specific", "raw_id": "preserved", "source_id": "actual", "locator": "row:1"},
  "right": {"namespace": "source-specific", "raw_id": "preserved", "source_id": "actual", "locator": "row:2"},
  "relationship_proposed": "same-entity/site/owner/officer/other",
  "method": "exact-value/fuzzy/crosswalk/original-record",
  "effective_period": "documented or unknown",
  "status": "candidate",
  "support": [],
  "contrary_evidence": [],
  "missing_decisive_record": "specific item"
}
```

This is a research sidecar, not an additional schema enforced by the case CLI.

## Synthetic collisions

Two entities named Synthetic Care LLC in different jurisdictions are not the same legal person merely because a fuzzy score is perfect. A single ID duplicated across two years is not two entities. An authorized official listed for several organizations may be an administrator; use actual ownership/control records for the stronger edge. Never skip the temporal or relationship question to produce a cleaner graph.
