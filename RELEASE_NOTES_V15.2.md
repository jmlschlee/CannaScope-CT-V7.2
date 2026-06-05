# CannaScope CT V15.2.0

A performance + data-durability release. CannaScope now keeps a **persistent, triple-verified COA
measurement cache**, ships **with the validated COA data baked in**, reviews **several products in
one consumer report**, and re-runs dramatically faster. All prior releases remain live and unchanged;
nothing was removed from the repository. Detection/validation logic is unchanged (`ANALYSIS_VERSION`
stays 15.1.0) — this release changes how data is *stored and reused*, not how it is judged.

## Added

### Persistent COA → measurement cache (`coa_csv_cache.py`)
A COA PDF is immutable once issued, so its **measurements never change** — only the threshold-dependent
**flags** vary run to run. CannaScope now caches the extracted measurements (one spreadsheet-readable
CSV row per COA in `COA Data Cache.csv`) so each COA is downloaded + read (including OCR) **once**.
Later runs reload the measurements and **recompute flags** from them, which means:

- **Re-runs are ~8× faster** (a warm statewide window dropped from ~37s to ~4s in testing), and
- **Lowering `--threshold` re-flags previously-clean COAs straight from cache** — no re-download, no
  re-OCR. (Verified: a yeast & mold result of 1,200 CFU/g, clean at the 10,000 standard, correctly
  re-flags at a 1,000 threshold entirely from cache.)

Opt in on a statewide run with `--csv-cache`. The cache stores flat columns (product/producer/brand/
lab/date/result/…), lossless JSON columns (`analytes`, `solvent_hits`, `cannabinoids`), and provenance
meta (`_method` = pdfium/pdfplumber/ocr, `_pdf_sha1`, `_cached_at`, `_schema`). Flags are never stored —
they are recomputed each run. A row is re-extracted only when the schema changes, the registry's COA
URL for that batch changes (a re-tested/re-released lot), or the prior read produced nothing.

### `build-cache` subcommand — full-registry analyze · TRIPLE-verify · save
`python3 CannaScope_CT_V15.py build-cache` walks the **entire product registry** (as far back as it
goes), downloads + reads each COA once, and **triple-verifies** every measurement before trusting it:

1. **Source-extracted** — every value carries a raw token parsed from the COA's own text (ND/limit/LOQ
   are never published as measurements);
2. **Source-bound** — the COA is confirmed to belong to that product (identity/registration match);
3. **Round-trip** — the measurements reload from the CSV and reproduce byte-identical flags.

It is resumable (a cached, unchanged COA is skipped instantly), checkpointed (atomic CSV flush every
250 COAs), and produces no PDF — it is the one-time data build. **This release ships with that
triple-verified COA data embedded**, so the program comes with the validated measurements already in
hand; new or re-released COAs are still fetched live and merged on later runs.

### One combined consumer report for several products
The Consumer Concern report now reviews **multiple products in a single PDF** (`concern
--products-json <file>`), with a shared header, a per-product section each, and an optional
`--conditions` field to record a consumer's reported health context for the reviewer (advisory only,
never medical advice). Sibling-COA lookups now run concurrently.

## Changed / faster
- **Persistent OCR-text cache** — an image-only COA is OCR'd once ever (content-hash keyed); re-scans,
  `audit-cache`, and `--force-rescan` skip re-OCR entirely.
- **Auto-sized OCR concurrency** — the default scales to the machine (`min(cores−2, 6)`) instead of a
  fixed 4; the low-memory serialize guard still applies.
- Declared version bumped to **15.2.0** (cover, footer, metadata).

## Unchanged / preserved
Detection thresholds, the date-aware legal verification, the COA source-binding six-field triple-check,
the three-part potency review, conflicting-COA review, per-run report folders, and the global report
numbering are all as in V15.1. No files, branches, tags, or releases were deleted or renamed.
