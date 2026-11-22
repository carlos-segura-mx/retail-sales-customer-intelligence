# Legacy Power BI implementation notes

**Caution:** This historical guide assumes private, line-level fact and dimension files that are intentionally not shipped in the public package. For a privacy-preserving public Power BI demonstration, use `POWER_BI_DESKTOP_HANDOFF.md` and `DESKTOP_VALIDATION_CHECKLIST.es.md` with disconnected aggregate tables. No Power BI model is currently validated.

# Power BI implementation and Desktop validation checklist

**Status:** Power BI files were not generated or opened in Power BI Desktop. This is a build specification, not a `.pbix` or verified deployment.

1. Import `fact_transaction.csv.gz` (decompress to CSV first), `dim_product.csv`, `dim_customer.csv`, `dim_country.csv`, `dim_date.csv`.
2. Set `line_key` whole number; `invoice_id`, `product_id`, `customer_id`, `country`, `date_key` as text. Disable auto date/time.
3. Create single-direction, many-to-one relationships: Fact[product_id] → Product[product_id]; Fact[customer_id] → Customer[customer_id]; Fact[country] → Country[country]; Fact[date_key] → Date[date_key]. Validate uniqueness of dimension keys and blank-key behavior.
4. Paste draft measures from `measures.dax`. Validate against `metrics.json` and monthly.csv.
5. Page 1 Executive: positive sales, cancellation value, analytical net, cancellation ratio, month trend, country mix, visible caveat banner.
6. Page 2 Product: ABC distribution, ranked products, review-flag filter, contribution vs. cumulative share; label `M`/service codes as unverified.
7. Page 3 Customer: RFM segment matrix, recency distribution, cohort candidate view, no fabricated churn probabilities.
8. Page 4 Action Center: priority, evidence, next test, proposed success metric, decision owner placeholder.
9. Confirm all slicers and measures reconcile with the supplied CSVs. Verify partial-month labels and refresh path. Publish only after privacy and data-license review.

**Data security:** Source customer identifiers are pseudonymous, but do not assume that means no re-identification risk. Prefer aggregated public demo data.
