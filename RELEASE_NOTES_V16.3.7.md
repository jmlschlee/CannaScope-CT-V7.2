# CannaScope CT V16.3.7

**Critical data-integrity fix — stops cross-attribution of COA results between products.**

## The bug
A report could publish one product's lab results under a *different* product's name. Example: a registry
record (“Seraden Wax”, MMBR.0000774) linked to a COA document that is actually a multi-product **Scott's
OG** report — “Seraden” appears nowhere in it. The report published Scott's OG's failing Yeast & Mold
(3,000,000 CFU/g) **as Seraden Wax's result**. The value really is in the linked PDF, so the existing
“every value re-verified in the linked COA” check passed it — but it was the *wrong product's* value.

## Two root causes (both fixed)
1. **Stale OCR cache.** When the OCR page cap was raised (6 → 40 pages) the OCR-text cache version wasn't
   bumped, so truncated **6-page** OCR text was reused for long scanned COAs. Multi-product documents then
   showed only their **first** product, so the multi-product splitter/suppressor never engaged and the
   first product's values were attributed to the registry record.
   **Fix:** `OCR_CACHE_VERSION` 1 → 2 — forces a full re-OCR so every product block is visible.
2. **Publish gate too permissive.** `validate_coa_row` granted a publishable “Verified Partial Match”
   whenever a flagged *value* appeared anywhere in the COA — even when the COA clearly belonged to a
   different product. Value-presence catches OCR/parse hallucination but **not** cross-attribution.
   **Fix:** new `_coa_is_different_product()` cross-attribution guard — if the COA prints product
   description(s) and **none** overlap the registry record's name, the row is marked **COA Product
   Mismatch** and routed to manual review (NOT published), regardless of whether a value appears.

## Effect
- Mis-linked and multi-product COAs whose product doesn't match the registry record are no longer
  published; they go to the COA Product Mismatch / review queue.
- Genuine matches are unaffected (a product whose COA really is its own still publishes; ID-only COAs with
  no printed product description still pass as partial).
- The embedded offline COA cache was **rebuilt for 2015–2021** with full re-OCR + the new gate, so the
  bundled dataset no longer carries these cross-attributed values.

## Verification
On the exact reported case: “Seraden Wax” vs the Scott's OG COA → **COA Product Mismatch (not published)**;
the multi-product splitter **suppresses** it; a product genuinely present in the COA still verifies; an
ID-only COA still passes as partial (no over-suppression). `ANALYSIS_VERSION` → 16.3.7.

All prior releases remain live.
