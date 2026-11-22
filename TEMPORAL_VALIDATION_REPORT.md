# CASE-03: Out-of-Time Basket Validation

**Status:** v1.3, executed on real UCI Online Retail II data. No causal, profit, Power BI Desktop, or live deployment validation is claimed.

## Executive finding

A historical basket-affinity ranking is vulnerable to selection bias and time instability. We therefore selected the 100 leading positive merchandise-candidate SKUs using **training data only**, assigned each invoice to a single period using its earliest merchandise transaction date, and recalculated associations on a subsequent period.

- Cutoff: **1 June 2011**.
- Training universe: **27,810** distinct positive merchandise-candidate invoices; **£13,745,077.38** positive candidate sales.
- Subsequent holdout: **11,706** invoices; **£6,362,634.69** positive candidate sales.
- Training candidate pairs with at least 30 joint invoices: **4,363**.
- Pairs passing the exploratory holdout screen: **2,662 (61.01%)**.
- Holdout screen: at least 20 joint invoices in holdout **and** lift >= 1.5 in each period.

## Why the methodology changed from v1.2

The v1.2 affinity analysis selected the top 100 SKUs using the full sample and computed lift over invoices containing at least one selected SKU. The new validation instead (1) selects the top 100 on training revenue only and (2) uses **all positive merchandise-candidate invoices** as the period-specific denominator. Thus **v1.2 lift figures and v1.3 lift figures are not directly comparable**. v1.2 remains an exploratory historical analysis; v1.3 is preferred for candidate selection.

## Managerial interpretation

The 2,662 surviving pairs are **screened hypotheses**, not independently verified opportunities. A commercially useful next decision is to shortlist pairs based on holdout co-purchase volume, availability, gross margin, distinct customer reach and product substitutability. Then randomize product recommendations or adjacency with a holdout and measure incremental gross profit per eligible basket. We cannot infer profit, incrementality, stockout risk or causal effects from these records.

## Methodological limits

- Product status is a rule-based *merchandise candidate*, not verified against a stock master.
- Positive merchandise lines only; cancellation matching and net merchandise accounting are not validated.
- The dataset is historical and reflects one retailer; it is not representative of current demand.
- Temporal validation does not adjust for seasonality, multiple comparisons, product availability or promotions.
- A passing pair may be a variant/substitute, not a useful bundle.
- All values are GBP. No price elasticity or contribution margin is estimated.

## Reproduce

```bash
python src/temporal_validation.py
streamlit run dashboard.py
```

The dashboard is a **Streamlit executive demo**, not a `.pbix`. DAX measures and Desktop setup notes are draft materials in `powerbi/`; native Power BI Desktop validation is pending.
