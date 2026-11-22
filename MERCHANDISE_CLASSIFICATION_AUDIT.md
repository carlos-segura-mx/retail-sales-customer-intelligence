# CASE-03: Merchandise classification audit (v1.1)

**Evidence:** UCI Online Retail II, both worksheets, 1,067,371 lines. This audit groups the 1,041,670 positive-sale lines by stock code and observed descriptions, preserving gross positive sales of **£20,972,594.55**. The classification is a **transparent heuristic**, not a validated stock master or accounting reclassification.

## Financial bridge

| Bucket | Codes | Positive sales (GBP) | Interpretation |
|---|---:|---:|---|
| Merchandise candidates | 4,875 | 20,107,712.07 | Regular stock-code patterns, no obvious service descriptions |
| Non-merchandise under explicit rules | 21 | 861,682.50 | Manual adjustments, postage, platform fees, carriage, vouchers and similar |
| Manual review | 20 | 3,199.98 | Ambiguous descriptions or unusual/mixed prefixes |
| **All positive-sale lines** | **4,916** | **20,972,594.55** | Reconciles to original gross positive sales |

**Scope:** All amounts are positive-sale line values, not net sales or margin. Cancellations remain in the separate original financial reconciliation. A rule-labeled non-merchandise line is not evidence of a confirmed accounting treatment. The review queue is mandatory before operational deployment.

## Revised merchandise-candidate ABC

| ABC | Codes | Positive sales (GBP) | Share of candidate sales |
|---|---:|---:|---:|
| A | 1,035 | 16,086,216.32 | 80.0002% |
| B | 1,278 | 3,016,571.16 | 15.0021% |
| C | 2,562 | 1,004,924.59 | 4.9977% |

ABC uses cumulative sales **before** each item to avoid splitting the boundary item and is computed only over merchandise candidates. The candidate set has not been validated against a product master.

## Rules and exceptions

1. Explicit code mappings classify `M`, `DOT`, `POST`, `AMAZONFEE`, `C2`, `BANK CHARGES`, `D`, etc. as non-merchandise *under the documented rule set*.
2. `GIFT_` prefix is treated as voucher/service under the rule set; `DCGS` is **not** automatically a voucher because actual descriptions include physical goods. All `DCGS` codes are flagged for review.
3. Regular numeric and number-plus-letter stock codes with no clear service description are *merchandise candidates*, not verified SKUs.
4. Keywords are deliberately narrow to avoid false positives: `FRENCH CARRIAGE LANTERN` and `BLACK BAROQUE CARRIAGE CLOCK` must not be classified as shipping merely because they contain *carriage*.
5. Shipping descriptions such as `Next Day Carriage` are flagged for manual review.
6. Product descriptions are preserved as evidence, including variations; the highest-revenue observed description is used as display label, not as a master-data correction.

## Decision implications

- **Assortment:** protect availability of A merchandise *candidates*, but confirm actual SKU identity, margins, stockouts, seasonality and lead times before buying decisions.
- **Pricing:** separate service charges and manual adjustments from merchandise revenue before estimating product price performance. This dataset cannot identify price elasticity causally.
- **Data governance:** validate review queue and mapping with a product master; add reviewer, disposition, rationale and version/date to a future classification register.
- **Experiments:** prioritize inventory availability or cross-sell pilots using margin, constraints and holdout design, not gross sales alone.

## Reproducibility and controls

Run `python -m src.merchandise_audit` after producing `outputs/classified_lines.csv.gz`. The script writes `product_classification_audit.csv`, `product_description_evidence.csv`, `classification_bridge.csv`, `classification_review_queue.csv`, `merchandise_candidate_abc.csv`, `merchandise_abc_summary.csv` and `merchandise_metrics.json`. Assertions verify gross-sales reconciliation, 4,916 codes, 1,041,670 positive lines and ABC sums.

**Power BI Desktop, stock-master confirmation, customer profitability and actual intervention outcomes remain unverified.**
