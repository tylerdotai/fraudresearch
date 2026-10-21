# Reconciliation and worked examples

## Required reconciliations

Compare component totals to published totals; versions for the same reporting date; transactions to cumulative award totals; payment records to reversals/refunds; and matched versus unmatched joins. A revision may be reclassification, corrected reporting or changed scope—not newly paid cash. Preserve both versions and the missing explanation.

| Pattern | Likely analytical trap | Required check |
|---|---|---|
| Same amount on debit/credit/interfund lines | Counting accounting legs as multiple losses | Transaction purpose, fund/code/description and linked journal entry |
| Identical invoice amount repeated | Duplicate publication or adjustment | Invoice/payment ID, status, reversals and bank/ledger linkage |
| Actual exceeds displayed budget | Missing amendments or timing | Applicable approved/amended budget, transfers and period |
| Award/action rows sum too high | Cumulative totals counted repeatedly | Grain and transaction-versus-total definitions |
| Outlier rate for small provider | Small denominator/cohort mismatch | Numerator, denominator, suppression, period and comparable cohort |

## Synthetic example: many-to-many inflation

A synthetic payment table has one payment for a provider; an ownership table has several owners. Joining then summing payment once per owner inflates expenditure. Verify the relationship grain and keep the payment total at its original transaction grain. Ownership multiplicity is not additional cash flow. Use tools for actual numbers; no mental arithmetic is required to detect the conceptual error.

## Synthetic example: suppressed values

A source uses a suppression marker for small counts. Treating it as zero changes the denominator and can manufacture an outlier. Preserve unknown/suppressed status and show whether the proposed comparison remains interpretable. Do not impute a precise value unless an explicitly justified method and uncertainty are part of the analysis.

## Amount labels

`Observed payment` means an attributable paid record supports it. `Questioned amount` needs a stated analytical basis and unresolved uncertainty. `Established loss` needs authoritative/evidentiary support beyond unusual spending. `Recovered` requires a refund/credit/settlement record; an accounting receivable is not proof of repayment. Never net or combine categories merely to produce a larger number.

## Interpretation gate

A numerical anomaly supports further investigation only if units, identity, period and coverage survive challenge. Check operational changes, legitimate program rules, prior corrections and selection effects. Report negative or inconclusive results rather than tuning thresholds until someone appears suspicious.
