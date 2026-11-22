# Methods and analytical contracts

## Source and line-level rules

The underlying source is Online Retail II (UCI), with two Excel worksheets and 1,067,371 original transaction lines. The source ingestion classifies positive sale lines, cancellations, zero prices, negative-price records and exceptions without silently deduplicating invoice lines. `outputs/metrics.json`, `outputs/quality_summary.csv`, `outputs/monthly.csv` and `outputs/classification_bridge.csv` document independently reconcilable figures.

The analytical convention is **positive sale value minus cancellation value**, not matched-return accounting. No net profit or actual contribution margin can be calculated.

## Candidate merchandise and ABC

A rule-based review separates likely merchandise from service or adjustment codes, while preserving an exceptions category. `outputs/merchandise_candidate_abc.csv` ranks candidate merchandise by positive sales value. It has **4,875 codes**, of which A contains 1,035 codes representing about 80% of candidate sales. This is not a verified stock master, nor a margin ranking.

## Customer analysis

RFM groups are calculated from historical positive sales involving identified customers. The repeat-customer measure uses at least two distinct positive merchandise invoices; 4,234 of the 5,852 identified merchandise buyers meet this definition. Other customer measures may use a broader positive-sales universe, so their denominators must not be combined without adjustment. Unidentified buyer sales are explicitly disclosed.

## Basket affinity and temporal holdout

The study selects the 100 highest-grossing candidate SKUs on the **training period only**. Invoice-to-period assignment uses the earliest candidate-merchandise positive line. The cutoff is **1 June 2011**, with 27,810 training invoices and 11,706 holdout invoices. A pair passes the exploratory screen if it has at least 30 joint training invoices, at least 20 joint holdout invoices, and lift of at least 1.5 in both periods. **2,662 pairs** pass out of 4,363 training pairs with sufficient training frequency. The screen does not adjust for multiple comparisons and cannot establish causal promotion effects.

## Decisions and experimentation

Product review lists translate observed recurrence, buyer concentration and co-occurrence into testable hypotheses. Recommendations depend on stock-master verification, margins, costs, inventory, eligibility and a properly randomized control group. Never treat hypothetical actions or high lift as observed incremental profit.

## Public package reproducibility

`python validate_release.py` runs 13 aggregate reconciliations and `python -m pytest -q` runs synthetic fixtures and publication checks. Full raw-data regeneration requires the two-sheet original Excel downloaded and transformed into the expected source-line schema, as described by the original `src/` pipeline. The public package intentionally excludes source invoices and customer-level extracts.
