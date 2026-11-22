# CASE-03: publication handoff, v1.5 candidate

The original v1.4 public demo has been adapted to a bilingual `app.py` entry point. The package includes six executive sections, aggregate-only outputs, extended tests and a GitHub Actions workflow.

## GitHub release

1. Create a public repository named `retail-sales-customer-intelligence` under the intended GitHub account. Do not initialize it with README or license, as the release already contains a README.
2. Upload the **contents** of the supplied public ZIP to the repository root, preserving the `outputs/`, `docs/`, `src/`, `tests/`, `powerbi/` and `.github/workflows/` paths.
3. Ensure `.github/workflows/quality.yml` succeeds. A green workflow does not substitute for manual dashboard inspection.
4. At https://share.streamlit.io/ select the repository, `main`, `app.py` and deploy.
5. Open all six sections in Spanish and English, test filters and CSV exports, and verify visible amounts against the `README.md` and `validate_release.py` output.
6. Once the public URL is verified, add it to both READMEs and capture a real screenshot for the professional portfolio.

## Power BI Desktop

No native Power BI report has been created or validated by this release. If Power BI is part of a specific gig or client deliverable, follow `powerbi/DESKTOP_VALIDATION_CHECKLIST.es.md`; build an independent aggregate-first PBIX and verify its measures, totals, filters and refresh in Power BI Desktop before offering it as a completed sample.

## Publication boundary

Never upload the development ZIP, the original UCI Excel, `fact_transaction.csv.gz`, individual customer files or other line-level extracts. The public ZIP already contains the permitted precomputed aggregates, an executive Excel workbook based on aggregates and the source code for reproduction when the original data are obtained separately.
