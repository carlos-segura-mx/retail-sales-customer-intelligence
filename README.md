# Retail Sales & Customer Intelligence

**How can a retail team use transaction data to decide which products and customer relationships deserve attention?**

[English](README.md) | [Español](docs/README.es.md) | [Methodology](docs/methodology.md) | [Data and limitations](docs/data_provenance.md)

This independent case studies real, historical **Online Retail II** transactions. I used line-level quality rules, a conservative merchandise-candidate classification, customer purchase summaries and an out-of-time basket analysis to turn descriptive patterns into questions a commercial team could investigate.

The dataset is not a client engagement. It contains neither product costs nor verified inventory, so the case does not claim actual profitability, churn predictions or promotional uplift.

## What the analysis found

| Historical result | Observed value |
| --- | ---: |
| Source transaction lines, across two original sheets | **1,067,371** |
| Positive sales recorded on classified sale lines | **£20.97 million** |
| Cancellations reported separately | **£1.53 million** |
| Sales assigned to merchandise-candidate codes | **£20.11 million** |
| Merchandise-candidate codes | **4,875** |
| Identified customers buying candidate merchandise | **5,852** |
| Item pairs passing an exploratory out-of-time screen | **2,662** |

The candidate-merchandise ABC classification shows that **1,035 A-class codes account for approximately 80% of candidate-merchandise positive sales**. Customer analysis identifies **4,234** repeat purchasers among the **5,852** customers with identified candidate-merchandise purchases. A separate RFM summary flags **396** high-spend, less-recent customers for investigation, not as predicted churners.

For cross-sell analysis, the 100-product universe was selected using the training period only. **2,662 pairs** met minimum frequency and lift rules in both the training and later evaluation periods. Passing this screen makes a pair worth investigating, not a proven profitable bundle.

## What decisions this supports

The case helps a planning team decide where to check product classifications, where buyer concentration or recurrence warrants attention, and which product combinations could justify a small controlled experiment. The next step would be to verify costs, availability, catalog definitions and implementation feasibility before acting.

## Interactive dashboard

Run the bilingual Streamlit app from `app.py`. Its six sections cover executive results, product ABC, customer behavior, basket affinity, a product-review center and methodology.

[Open the live Streamlit dashboard](https://retail-sales-customer-intelligence-pyazdmafnsbevcbqpoxmud.streamlit.app/). The Spanish overview has been visually confirmed from the deployment screenshot supplied by the project owner. The remaining tabs and English interface have automated smoke-test coverage but have not yet been visually reviewed in full. A `dashboard.py` script was used in the earlier v1.4 prototype; `app.py` is the publication entry point.

```bash
python -m pip install -r requirements.txt
python validate_release.py
python -m pytest -q
streamlit run app.py
```

The repository contains a curated **aggregate-only** public dataset in `outputs/`. The original Excel, transaction-line extracts and identifiable customer records are excluded. This means the published QA can reconcile the aggregates, but the complete ingestion pipeline needs the separately downloaded source data. See [data and reproduction notes](docs/data_provenance.md).

## Important interpretation limits

- The **£20.97 million** is positive line value, not audited accounting revenue. Cancellation values are not matched to originating sales; other price adjustments are reviewed separately.
- Merchandise-candidate classification relies on code and description rules. It has not been validated against a physical stock master.
- ABC is measured by recorded positive sales, not profit. Customer segments describe historical purchases, not future customer behavior.
- Lift measures basket association, not causal incremental sales. No promotion experiment was conducted.
- Power BI Desktop implementation is **not verified**. Aggregate-first model instructions and draft DAX are provided in `powerbi/`, but there is no validated `.pbix` in this public release.

**Data attribution:** Chen, D. (2012), *Online Retail II*, UCI Machine Learning Repository, [DOI: 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No separate open-source license has been selected for the original code in this repository.

**Carlos Segura | CS Intelligence**
