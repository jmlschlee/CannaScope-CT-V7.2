# CannaScope CT V16.3.2

**Multi-product COA recognition — additive, safe.** Some 2015-era Connecticut COA documents (notably the
Northeast Laboratories, Inc. "Analytical Report" PDFs) pack SEVERAL products into one document. This
release teaches CannaScope to recognize and surface those documents, and ships a validated per-product
splitter. **Detection/surfacing only on the published path — no finding is added, removed, or changed;
`ANALYSIS_VERSION` stays 16.3.0.**

## What's new
- **Generalized multi-product detection.** Learned from a confirmed real 2015 Northeast Labs COA. The real
  signal is an **incrementing Laboratory ID # suffix** (`1562829-01, -02, …`) and/or multiple distinct
  Product Descriptions in one document — not the data.ct.gov-era `MMBR` registration number (absent in the
  old lab format), which the prior detector relied on. Two layouts are distinguished:
  - **Layout A** — one product, one analyte *panel* per page (Laboratory ID # constant) → pages are
    COMBINED.
  - **Layout B** — many products, one *product* per page (Laboratory ID # increments) → products are
    separated.
- **Validated per-product splitter** (`cannascope_multiproduct.py`, pure-stdlib, embedded in the
  single-file build). Groups pages by Laboratory ID #, and `isolate_product()` returns a single product's
  block ONLY on a confident unique match (exact Lab ID / product description / unique "#N" marker);
  otherwise it returns nothing and the record is **routed to manual review** rather than guessed — so one
  product's contaminants can never be attributed to another.
- **Surfacing.** New debug metrics `multi_product_coa_documents` and
  `multi_product_coa_products_recognized`; self-audit observation and glossary updated.

## Why detection-only for now
Substituting an isolated per-product block into the published extraction changes findings and requires a
per-record statewide regression confirming zero cross-attribution, plus a fix to the OCR page-depth cap so
every product page is read. That enablement is tracked as the next release; this one is strictly additive
and safe.

All prior releases remain live. Validated by `_test_multiproduct.py` (17 checks) and the existing
`_test_report_integrity.py` suite.
