# CASE-03: publication readiness, v1.5 candidate

## Verified from the public aggregate package

- Historical Online Retail II analysis and aggregate tables retained from v1.4.
- Thirteen aggregate release reconciliations, four original synthetic tests, and additional public-data/editorial checks can be executed locally.
- Bilingual Streamlit publication app located at `app.py`; Spanish and English introductory copy and methodology are available.
- No original invoice lines, customer IDs, confidential contact details, original raw Excel or private development exports are packaged.

## Must still be verified

- Streamlit installation and interactive AppTest in GitHub Actions or a suitable local environment. This authoring runtime cannot install Streamlit; do not mark browser checks as complete.
- User-created GitHub repository, automated workflow status and deployed public URL.
- Visual inspection in Streamlit Community Cloud for each tab, data exports, product filters, both languages and mobile widths.
- Optional native Power BI Desktop `.pbix` build, refresh, model relationships and totals if offering Power BI services.

## Interpretation limits

The merchandise taxonomy is rule-based and unverified against a stock master. Cancellations are not linked to origin invoices. The out-of-time basket screen is descriptive and exploratory. The source does not allow claims of contribution margin, inventory optimization, causal incremental revenue or churn prediction.
