# Award-data contracts and implementation limits

## Implemented agency reference

`uv run fraudlab connector agencies` calls:
https://api.usaspending.gov/api/v2/references/toptier_agencies/

Publisher contract:
https://raw.githubusercontent.com/fedspendingtransparency/usaspending-api/master/usaspending_api/api_contracts/contracts/v2/references/toptier_agencies.md

The response contains `results`, agency identifiers/names, active fiscal year/quarter and agency budgetary fields. `agency_id` is a USAspending identifier, not a recipient/award ID. The contract describes `percentage_of_total_budget_authority` as a decimal value. These records do not document a provider award or invoice.

## Award-level discovery contract

Before implementing or using another route, inspect its current official contract: HTTP method, request parameters, recipient/award identity, fiscal/service dates, pagination, totals, null/negative handling, rate/access requirements and transaction grain. A client-side loading shell is not retrieved methodology; verify that the actual source content was acquired.

No award-level automatic connector is currently installed. A generic CSV import can preserve a qualified official download but is not proof of full USAspending integration. A read/search POST is not automatically approved by generic GET research authority; obtain applicable approval rather than guessing endpoint or payload semantics.

## Match checks

- Distinguish legal recipient, parent, DBA, fiscal sponsor and subrecipient.
- Preserve raw UEI/EIN/agency/award identifiers; validate formats before lookup and do not repair malformed tokens silently.
- Compare periods and effective amendments, not merely current names.
- Record whether a figure is an award total, action amount, ceiling or paid disbursement.
- Avoid summing cumulative snapshots or combining loan principal with subsidy measures as though both were losses.

For a funding assertion, cite the record supporting that exact recipient/program/transaction link. A project description mentioning a public goal or geographic area is not sufficient identity evidence.
