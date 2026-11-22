# CASE-03: Data dictionary and metric contract

**Grain:** one source worksheet row per fact row. Duplicate-looking source lines are not removed.

| Output | Grain | Definition / warning |
|---|---|---|
| quality_summary.csv | classification status | Counts and signed line values by deterministic quality class |
| monthly.csv | calendar month | Positive-sale value, units, distinct invoice IDs; first/last months may be partial |
| country.csv | source country | Positive-sale value and distinct invoice IDs |
| products_abc.csv | source product code | Positive-sale revenue, units, cumulative contribution, ABC; includes non-merchandise candidates |
| product_action_center.csv | product code | ABC plus provisional manual-review flag and action hypothesis |
| customers_rfm.csv | identified customer | Positive-sale recency, distinct invoice frequency, monetary value; relative quintiles |
| customer_action_center.csv | identified customer | Observational segment and experimental next-step hypothesis |
| abc_summary.csv | ABC band | Count and positive-sales contribution |
| rfm_segment_summary.csv | RFM segment | Customer count and positive-sales value among identified customers |
| fact_transaction.csv.gz | original source line | Transaction identifiers, keys, signed line value, gross positive, cancellation and net convention |
| dim_product.csv | product code | One selected description per code; description consistency not fully validated |
| dim_customer.csv | customer ID | Pseudonymous key; may not imply contactability |
| dim_country.csv | country | Raw country label; standardization not applied |
| dim_date.csv | calendar day | Continuous date spine |

## Metric definitions
- **Line value** = Quantity × Price, rounded to 2 decimal places at the source-line level.
- **Positive sales** = sum of positive-sale line values with positive quantity and strictly positive price, excluding cancellation-marked invoices.
- **Cancellation value** = absolute signed value for C-prefixed invoices with negative quantity and strictly positive price.
- **Analytical net** = positive sales − cancellation value; other adjustments excluded pending investigation.
- **Cancellation ratio** = cancellation value / positive sales; **not** a verified return rate or refund match rate.
- **ABC** = product code ranking by positive-sales value; cumulative shares using contribution *before* the current product at thresholds 80% and 95%.
- **RFM recency** = days from last positive purchase to the day after the latest positive sale in the dataset; quintile scores relative to identified customers.
- **RFM frequency** = distinct positive-sale invoice IDs per customer.
- **RFM monetary** = positive-sale amount per customer, ignoring matched returns.

## Quality gates
1. Source line count exactly 1,067,371.
2. Classification statuses partition source rows.
3. Positive sales = sum monthly = sum country = sum product, within £0.01.
4. Analytical net = positive sales − cancellation value, within £0.01.
5. No value-based deduplication of transaction lines.
6. All product and customer action labels are hypotheses pending external business context.
