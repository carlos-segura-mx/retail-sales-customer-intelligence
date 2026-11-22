# CASE-03: Retail Sales & Customer Intelligence
## From transaction records to defensible commercial decisions

**Dataset:** Online Retail II (UCI Machine Learning Repository; Chen, 2012, DOI: 10.24432/C5CG6D). Two source worksheets, 1,067,371 line records. **Currency:** GBP. **Status:** reproducible analytical case; Power BI Desktop implementation remains unverified.

### Management question
Which products and customers merit attention, what portion of recorded revenue is concentrated, and which interventions can be prioritized without confusing correlation with causation?

### Executive scorecard
| Measure | Observed |
|---|---:|
| Source lines | 1,067,371 |
| Positive sale lines | 1,041,670 |
| Cancellation lines | 19,493 |
| Zero-price lines | 6,202 |
| Negative-price review lines | 5 |
| Other cancellation-review lines | 1 |
| Positive sales | £20,972,594.55 |
| Cancellation value | £1,527,041.43 |
| Analytical net convention | £19,445,553.12 |
| Cancellation value / positive sales | 7.28% |
| Positive-sale product codes | 4,916 |
| Identified positive-sale customers | 5,878 |

**Reconciliation:** £20,972,594.55 − £1,527,041.43 = £19,445,553.12. Monthly, country and product positive-sales aggregations reconcile to the positive-sales total to penny tolerance. This is **not** an audited accounting reconciliation: negative-price adjustments and zero-price lines are excluded, and cancellation invoices are not matched to original orders.

### Commercial findings
**Portfolio concentration.** The initial ABC allocation identifies 1,005 A codes (80.02% of positive-sales value), 1,285 B codes (14.98%), and 2,626 C codes (5.00%). This is the preliminary *code-level* ranking, superseded for assortment screening by the audited candidate-merchandise ABC in `MERCHANDISE_CLASSIFICATION_AUDIT.md`. It is not a validated merchandise assortment: codes such as `M`, `POST`, and `DOT` require service/adjustment classification before purchasing decisions.

**Customer signals.** The observed positive-purchase RFM segmentation identifies 1,473 active/frequent customers, 396 high-value but less-recent customers, 651 frequent customers outside the first segment, and 3,358 other identified customers. The categories describe historical behavior at the dataset endpoint; they are not calibrated churn probabilities.

**Temporal interpretation.** The data span 25 calendar months, including partial opening and closing months. Compare full months and seasonally matched periods; do not interpret the final partial month as a sudden demand collapse.

### Decision architecture inspired by commercial analytics practice
1. **Measurement:** validate invoice lines, preserve duplicates, identify cancellations and adjustments, define gross/returns/net conventions.
2. **Diagnosis:** quantify concentration, customer recency/frequency/monetary value, country mix, monthly trajectory, and exception lists.
3. **Decision:** review high-sales-concentration candidate merchandise and protect availability only after inventory and margin validation, test retention treatments on eligible customer segments, review non-merchandise codes, and prioritize data-quality fixes.
4. **Experiment:** randomize eligible customer outreach vs. holdout; measure incremental contribution margin net of incentive, contact and fulfillment costs. Do not claim a campaign uplift from historical RFM alone.
5. **Monitoring:** refresh segments on a consistent cutoff, track actual vs. expected repeat purchases, document interventions and outcomes.

### Prioritized commercial backlog
| Priority | Decision | Evidence | Next validation | Success metric |
|---|---|---|---|---|
| P0 | Reclassify non-merchandise and adjustment codes | High-ranked `M` and service-like codes | Verify descriptions and source-system semantics | Clean merchandise revenue reconciliation |
| P1 | Protect top merchandise availability | ABC concentration | Remove service codes; add margin and inventory data | Contribution margin and in-stock rate |
| P1 | Run win-back pilot | 396 high-value/inactive-observed customers | Consent, contactability, holdout design | Incremental margin per eligible customer |
| P2 | Cross-sell pilot | 651 frequent customers in secondary RFM segment | Product affinity, margin, seasonality | Incremental basket margin |
| P2 | Review long-tail codes | 2,626 initial C codes | Cost-to-serve, lead times, strategic role | Margin after carrying cost |

### Important constraints
- `Invoice` is not a guaranteed order identity across all business contexts; positive orders should be validated against transaction semantics.
- RFM monetary is **positive sales only**, not customer net after matched returns.
- Customer IDs are pseudonymous identifiers in the source, not contactable CRM profiles.
- The source contains no cost, margin, stockout, marketing treatment, exposure, or counterfactual data; elasticity, profitability, retention lift and causality **cannot** be established.
- The published Power BI measures are implementation drafts and have not been validated in Power BI Desktop.

### Reproducibility
Run `python -m src.pipeline --source data/source_lines.csv --output outputs` from project root after extracting the source into the prescribed CSV structure. The original Excel remains outside the publication package. See `README.md`, `DATA_DICTIONARY.md` and `powerbi/measures.dax`.
