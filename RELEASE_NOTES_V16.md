# CannaScope CT V16.0.0

**The data-integrity release.** V16 ships a persistent, **triple-verified COA measurement dataset**
covering the entire Connecticut registry (≈33,692 Certificates of Analysis, 2015–2026) **baked into
the program**, and it fixes a family of real parser misreads — driving the measured misread rate from
**1.26% to 0.000%**, audited against the actual source COAs across every year. All prior releases remain
live and unchanged; nothing was removed, renamed, or force-pushed.

---

## Why this release matters
Roughly **30,000 Connecticut medical-cannabis patients** rely on the accuracy of this data. V16 was
built and audited to that standard: every fix was verified against the real source documents, and the
release ships with the validated data in hand so results are fast, consistent, and reproducible.

---

## 1. Parser accuracy — six engine fixes, audited to zero
A deep audit (1,000- and 1,200-COA document re-reads stratified across all years) surfaced six real
misread classes in the extraction engine. All are fixed at the root cause:

1. **Below-detection mistaken for a measurement** — a result like `<20` whose bound equals the limit
   was dropped *as* the limit, and the bare limit was kept as a false at-limit value. A comparator
   (`<`, `≤`) token is now always a result, never the limit.
2. **Limit column read as the result (generic rows)** — a bare value equal to its own action limit is
   now recorded as a conservative below-limit bound, not a false at-limit reading.
3. **Same, for detail-table rows** ending in a Pass/Fail word — the same guard now applies there too.
4. **Impossible microbial counts** — a garbled scan producing e.g. `4e14` CFU/g (400 trillion) would
   have fired a false **RED “do not consume.”** Any CFU/g ≥ 1e11 is now rejected as an OCR artifact.
5. **Δ9-THC capturing the THCA value** — “THC” matched inside “THC-A,” duplicating THCA into the Δ9-THC
   field and inflating Total THC past 100% (~192 concentrates). The label now excludes the acid form.
6. **Impossible derived Total THC** — when a derived Total THC still exceeded 100% (from an OCR-garbled
   decimal like `.049`→49 on an old scan), the COA’s THC potency is now dropped as *not reliably
   readable* rather than published as a wrong number.

**Audit result:** limit-as-value misread **1.26% → 0.000%**; storage fidelity **100%**; cannabinoid
>100% **192 → 0**; implausible microbial/metal, negatives, raw-without-digit all **0**. Critically,
**no genuine finding was lost** — a real exceedance is `value > limit` (a different, larger number),
which none of these fixes touch. The fixes *remove false positives*; they create no false negatives.

---

## 2. Triple-verified COA data, baked into the program
A new persistent measurement cache (`coa_csv_cache.py`) stores one spreadsheet-readable row per COA.
A dedicated **`build-cache`** pass walks the whole registry, reads each COA once (incl. OCR), and
**triple-verifies** every value before trusting it:

1. **Source-extracted** — the value carries a raw token parsed from the COA’s own text (ND/LOQ/limits
   are never published as measurements);
2. **Source-bound** — the COA is confirmed to belong to that product;
3. **Round-trip** — the measurements reload from storage and reproduce byte-identical flags.

Result: **33,692 COAs · 32,721 triple-verified · 419 double · 552 unreadable (queued for retry)** —
**embedded in the program** (like the registry snapshot) and auto-seeded on first run.

### What this buys you
- **Re-runs are ~8× faster** — measurements load from the dataset (~49,000 COAs/sec); no re-download,
  no re-OCR. A first-time user inherits the built dataset and never pays the ~70-minute cold build.
- **Change the threshold, re-flag instantly** — flags are recomputed from stored measurements, so
  lowering `--threshold` correctly re-flags previously-clean COAs with no reprocessing.
- **Works offline** — the program ships with the validated measurements in hand.
- Opt into it on a scan with `--csv-cache`; rebuild it any time with `build-cache`.

---

## 3. Multi-product Consumer Concern report
The consumer report now reviews **several products in one combined PDF** (`concern --products-json
<file>`), with a shared header, a per-product section each, and an optional `--conditions` field to
record a consumer’s reported health context for the reviewer (advisory only, never medical advice).
Sibling-COA lookups now run concurrently.

---

## 4. Performance + the web app
- **Persistent OCR-text cache** — an image-only COA is OCR’d once ever (content-hash keyed).
- **Auto-sized OCR concurrency** — scales to the machine (`min(cores−2, 6)`).
- **Streamlit web app updated to V16** (`streamlit_app.py`) — a friendly browser UI (one-product
  Consumer Concern lookup + a small Statewide sample) that drives the current program and serves the
  PDF via a download button. Deployable on Streamlit Community Cloud from `main`.

---

## Downloads
Three OS packages — `CannaScopeCT-V16-{Windows,macOS,Linux}.zip` — each contains the single
self-contained `CannaScope_CT_V16.py` (program + engine + the triple-verified COA dataset + registry
snapshot, all embedded) plus README, requirements, LICENSE, INSTALL, and per-OS run scripts. Just
unzip and run a script; no other files needed.

## Unchanged / preserved
Detection thresholds, the date-aware legal verification, the COA source-binding six-field check, the
three-part potency review, conflicting-COA review, per-run report folders, and the global report
numbering are all as before. `ANALYSIS_VERSION` stays 15.1.0 (detection *logic* is unchanged; this
release changes how data is stored, validated, and reused). All prior releases remain live.
