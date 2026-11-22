# Data provenance and public release boundaries

The underlying source is **Online Retail II**, by D. Chen (2012), from UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5CG6D. The dataset is described by UCI under **CC BY 4.0**, requiring attribution. The raw original Excel and invoice-line extracts are not redistributed in this project release.

The downloadable public package contains **aggregate tables only** from the approved v1.4 public demo, such as month totals, candidate-merchandise ABC, SKU-level buyer concentration summaries, RFM segment totals and SKU-pair association summaries. SKU and description labels come from the historic dataset; individual customer identifiers and original invoice lines are excluded.

The public QA checks **precomputed output consistency**, not a fresh ingestion of all original records. Recreating the outputs from scratch requires downloading the source Excel, parsing both sheets with source provenance and following the full pipeline stages. This repo documents the workflow, but does not package or claim a one-command raw-to-output regeneration from the reduced public zip.

**Limits:** candidate merchandise is heuristic; cancellations are not linked to origin invoices; source lacks cost, profit, inventory, stockouts, promotional treatment and customer contact permissions. The Power BI file is not provided as a validated native deliverable.
