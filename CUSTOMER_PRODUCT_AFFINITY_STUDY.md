# CASE-03: Customer Concentration, Repeat Purchasing & Basket Affinity

**Status:** v1.2 analytical extension, reproducible locally; no causal or Power BI Desktop validation claimed.

## Management questions

1. Which merchandise candidates depend disproportionately on a small number of identified buyers?
2. Which identified customers place multiple distinct positive-merchandise invoices?
3. Which frequently sold products co-occur in invoices often enough to warrant cross-sell experiments?

## Observed results

- Candidate merchandise positive sales: **£20,107,712.07**.
- Positive merchandise sales with customer identifier: **£17,433,249.98 (86.70%)**; the rest cannot be allocated to customers.
- **5,852** identified buyers; **4,234** have two or more distinct positive-merchandise invoices (**72.35%**).
- **4,618** candidate SKUs have at least one identified buyer. Buyer concentration ratios exclude unidentified sales; a separate coverage field is supplied.
- Basket-affinity universe: **31,382** distinct invoices containing at least one of the 100 highest-grossing merchandise-candidate SKUs. **4,769** unordered pairs meet the exploratory minimum of 20 co-occurring baskets. These are *not* 4,769 independently validated opportunities.

## Definitions and analytical controls

- **Positive merchandise:** `status == positive_sale` and `merchandise_status == MERCHANDISE_CANDIDATE` from v1.1 heuristic. This is not confirmed merchandise in a verified stock master.
- **Identified revenue coverage:** positive candidate merchandise sales with a non-null `customer_id` divided by all positive candidate merchandise sales.
- **Repeat buyer:** at least two *distinct invoice IDs* with positive merchandise, not two rows in the same invoice. No assertion about customer lifetime beyond observed dates.
- **Top-buyer share:** top identified buyer's sales divided by sales from identified buyers of the SKU. Do not confuse this with share of all SKU revenue.
- **Basket:** distinct `invoice_id`; line-level repeats are deduplicated to a set of SKU IDs for co-occurrence.
- **Support:** co-occurrence count / 31,382; **confidence A→B:** co-occurrence / A's basket count; **lift:** support(A∩B)/(support(A)×support(B)).
- **Selection bias:** 100 highest-positive-sales SKUs were preselected. Basket universe is restricted to invoices containing at least one selected SKU, so lift is conditional and is not a global all-product association measure.
- **Minimum support screen:** 20 co-occurring invoices. Stronger recommendations should require additional volume, margin, availability, seasonality and out-of-time validation.
- **No causal inference:** association is not incremental cross-sell uplift. Product variants, seasonal assortment and common customers may explain co-purchase.
- **Returns:** excluded from positive-sales affinity and customer frequency; original invoice matching remains outstanding.

## Action design: measurement → diagnosis → decision → test

| Observation | Decision hypothesis | Guardrail | Experiment |
|---|---|---|---|
| High top-buyer concentration | Diversify demand and monitor account dependency | Review unidentified-sales share and gross margin | Account-development program with pre-specified retention and diversification KPIs |
| Frequent repeat purchase | Investigate replenishment cycles | No claim of stable repurchase interval | Randomized reminder vs holdout; measure incremental gross profit |
| High co-purchase lift | Test product adjacency or relevant bundles | Check substitutability, margin, stock and calendar | Randomized basket recommendation; compare incremental contribution per eligible session |

## Public release and privacy

Only aggregate product metrics, anonymized SKU-to-SKU relationships and executive documentation are included. No individual customer IDs, customer-level orders or raw transaction lines are included in the release package. Verify original data licensing and repository distribution policy before publishing.

## Files

- `outputs/product_customer_concentration.csv`: per-SKU buyer concentration and coverage.
- `outputs/merchandise_repeat_summary.csv`: aggregate repeat-customer statistics.
- `outputs/basket_affinity_top100.csv`: directional confidence, lift, counts, descriptions.
- `outputs/merchandise_action_shortlist.csv`: 100 screened SKU hypotheses.
- `outputs/affinity_metrics.json`: concise reconciliation and definitions.
- `src/affinity.py`: reproducible analysis from v1.1 classified lines and classification audit.

**Next validation:** sensitivity to alternative SKU selection and basket universes, temporal holdout, cancellation linkage, verified stock master, Power BI Desktop and operational feasibility.
