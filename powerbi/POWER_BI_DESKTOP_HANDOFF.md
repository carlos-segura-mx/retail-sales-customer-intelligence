# CASE-03: Power BI Desktop build specification

**Status:** not implemented or tested in Power BI Desktop. Aggregate-first, privacy-preserving model.

## Public aggregate model (separate facts, no fabricated joins)

| Table | Grain | Main fields | Page |
|---|---|---|---|
| monthly | calendar month | month, revenue_gbp, units, orders | Executive |
| merchandise_abc_summary | ABC class | abc, product_codes, positive_sales_gbp | Assortment |
| classification_bridge | classification reason | merchandise_status, reason, positive_sales_gbp | Governance |
| rfm_segment_summary | RFM segment | segment, customers, observed_monetary_gbp | Customer |
| validated_affinity_shortlist | SKU pair | product_a, product_b, train/test lift and co-baskets | Experiments |
| merchandise_action_shortlist | SKU | product_id, revenue_gbp, buyer metrics, action_hypothesis | Action Center |

Do **not** join independent aggregate facts on invented keys. Use disconnected tables and page-specific measures. If building a detailed star schema, use the private fact and dimensions with an explicit privacy review; do not publish that data model.

## Measures (illustrative; validate after import)

```dax
Positive Sales GBP = SUM(monthly[revenue_gbp])
Candidate Merchandise GBP = SUM(merchandise_abc_summary[positive_sales_gbp])
ABC SKU Count = SUM(merchandise_abc_summary[product_codes])
RFM Identified Customers = SUM(rfm_segment_summary[customers])
Screened Pair Count = COUNTROWS(validated_affinity_shortlist)
```

**Warning:** `Screened Pair Count` counts the 100-row *prioritized shortlist*, not all 2,662 passing pairs. The full count is in `outputs/temporal_validation_metrics.json` and `outputs/basket_temporal_validation.csv`.

## Reconciliation checkpoints

- Positive sales across monthly and classification bridge: **£20,972,594.55**.
- Candidate merchandise across ABC classes: **£20,107,712.07**.
- Non-merchandise rule separated: **£861,682.50**.
- Review queue: **£3,199.98**.
- ABC SKU count: **4,875**.
- Full screened-pair count: **2,662**; prioritized shortlist: **100**.

## Required visual review

- GBP number format; chart labels; non-overlapping cards; filters; month ordering; partial-month notice.
- Clearly label candidate merchandise vs confirmed stock; no churn prediction or causal lift claim.
- Test Desktop refresh from local CSV paths; export screenshots only after all totals reconcile.
