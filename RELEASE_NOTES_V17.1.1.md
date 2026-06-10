# 🌿 CannaScope CT — V17.1.1

**Source-verified Connecticut cannabis transparency reporting.** Every published number traces back to the product's own publicly linked Certificate of Analysis (COA). This release is a **honesty + readability + added-analysis** update — no measurement, threshold, limit, or finding logic was changed.

🔗 **Live web app:** https://cannascope-ct.streamlit.app &nbsp;·&nbsp; 💻 Desktop downloads below (Windows / macOS / Linux).

---

## 🆕 What's new in V17.1.1

### 🛰️ Honest live-verification coverage — now a *gate*, not just a counter
- Every report states on the cover how many products were **re-verified against their live source COA this run**.
- 🚦 If a run did **zero** live verification (offline, or everything served from cache), the cover is unmistakably stamped **`CACHE-REPLAY — NOT LIVE-VERIFIED THIS RUN`**, and **no finding is presented as live-verified**. Incidental OCR can no longer disguise a cache replay as a validated run.
- ✅ **Root-cause fix:** genuine live downloads (the normal ledger path) are now correctly **credited** as live verification — so a real online run shows real, non-zero coverage instead of a misleading "0%."
- 🔁 The "Live URL Verifications" counter was relabeled and a true **"COAs re-fetched LIVE this run"** counter added, so the numbers can't contradict each other.

### ⚡ New `--live-verify` switch
- Forces a fresh re-fetch of **every** COA from its source link this run (plus a full cache self-audit) for a fully live-verified report. The run log states `LIVE VERIFICATION: ON (forced)` / `OFF` in one plain line.

### 📈 New section — "Convenient Lab Result Groupings by Producer and Lab"
- A statistical screen that flags **statistically unusual clustering of results just *below* a pass/fail limit**, grouped by **producer + lab + analyte** (primary target: **yeast & mold** near the 100,000 CFU/g limit).
- 📊 Per group: total / near-threshold (95–100% of limit) / over-limit counts, observed-vs-statewide-expected, **binomial p-value, z-score, chi-square goodness-of-fit, Fisher exact (small samples), a cliff-effect check, and a transparent Convenience Score (0–100)**.
- 🧾 Includes a plain-English column legend, a public Top-10 summary, a full statistical appendix (methodology + per-grouping detail + scatter), and a `convenient_lab_result_groupings.csv` export.
- ⚠️ **Review signal only — never a fraud claim.** Boundary clustering can come from legitimate retests, remediation, sampling, rounding, reporting, or selection effects.

### 🏷️ Renamed for accuracy
- "Potency Parser Conflicts" / "Impossible Cannabinoid Math" → **"Laboratory Data Consistency Flags"** (data-integrity alerts about a COA's own numbers — Total THC > Total Cannabinoids, etc. — **not** software errors).
- "High THC Flower Review" → **"Biologically Implausible High THC Flower Review."**

### 📊 Coverage Integrity Summary
- A standing table — COAs **expected / acquired / parsed / live-verified** with acquisition, parse, and verification ratios — that **fails loud** if any denominator is zero or the buckets don't reconcile.

### 🧹 Cleaner, more readable report
- 🪪 **Decluttered cover:** status tier, headline counts, one warning line, one pointer — the diagnostic banner, validation counters, severity legend, and definitions are relocated to the Technical Validation & Diagnostics appendix.
- 🎯 **Centered, larger, easier to read:** "Most Important Findings," "Statewide Snapshot," and "How To Read These Findings."
- 🥇 **Ranked, tier-banded "Flagged Findings by Producer":** a Rank column + bands (**Highest review priority ≥ 20% · Moderate 10–20% · Low < 10%**), sorted by % flagged, with the rule printed.
- 🧷 **No orphaned headers** — every section header stays with its table.
- 🧫 **Pathogen findings sorted newest → oldest.**
- ✂️ **Front technical summary compressed** to two short lines (full breakdown in the appendix).

### 🔤 Rendering
- `µg/kg` and other glyphs render correctly in **every** PDF viewer (embedded Unicode font) — no more "g/kg" drops or missing-glyph boxes.

---

## ✨ Full feature set (what CannaScope CT does)

### 📋 Two ways to use it
- 🔎 **Look up a product** by name / brand / batch / COA number → plain-English PDF.
- 🏛️ **Statewide transparency report** over any date window → one downloadable PDF.

### 🧪 Reads from each COA
🦠 microbials (yeast & mold, aerobic bacteria, pathogens) · ⚗️ heavy metals (As, Cd, Pb, Hg, Cr) · 🌾 pesticides · 🧴 residual solvents · 🍞 mycotoxins · 🌿 cannabinoids/potency · ✅/❌ pass-fail.

### 🛡️ Accuracy & honesty guarantees
- 🔗 Every published value re-verified against the product's **own** linked COA.
- 🛰️ **Live-first, live wins** — cache is a speed hint, corrected when live disagrees.
- 🧬 **Multi-product COA isolation** — never cross-attributes one product's results to another.
- 📅 **Date-window integrity** — only in-window COA test dates published; out-of-window data **aborts** the run.
- 🔬 **OCR up to 5 escalating attempts**; uncertain values **held for review**, never guessed.
- 🧫 **Below-detection aware** (`<X` treated as a bound, not a failure).
- 🚦 **Fail-loud:** empty report, out-of-range data, or non-reconciling accounting **stops** the run.
- 🖥️ **Cross-platform** (macOS / Windows / Linux).

### 📚 Context & analysis
📜 per-year CT standards 2015–2026 with citations + live re-consult · 🏛️ patient-safety / ombudsman review · 🔁 conflicting-COA detection (side-by-side) · 📊 ranked producer & lab summaries · 📈 Convenient Lab Result Groupings (statistical) · 🧮 Laboratory Data Consistency Flags · 🌿 Biologically Implausible High-THC Flower review.

### 📦 Outputs & transparency
🧾 downloadable PDF · 📑 CSV exports for every section · 🧰 Technical Validation & Diagnostics appendix (Coverage Integrity Summary, validation counters, date-window integrity, source-binding & self-audit, parser/OCR diagnostics) · 💾 triple-verified COA cache (offline-capable, clearly labeled) · 🔢 provenance & per-value verification stamp.

---

## 🚀 Run it

```bash
# Statewide (live-first). Add --live-verify to force a fully live re-verified run.
python CannaScope_CT_V17.py statewide --since 2024-01-01 --until 2024-12-31
python CannaScope_CT_V17.py statewide --since 2024-01-01 --until 2024-12-31 --live-verify

# Single-product consumer report
python CannaScope_CT_V17.py concern --example
```

Each OS zip below bundles the self-contained `CannaScope_CT_V17.py` (embeds the triple-verified COA dataset) + README + requirements + LICENSE + INSTALL + double-click run scripts. Python 3.9+; `pip install -r requirements.txt`.

---

## ⚖️ Important
CannaScope CT is an **independent, informational transparency tool** — **not** medical, legal, or professional advice, and **not** affiliated with or endorsed by the State of Connecticut, any lab, or any producer. **Every flag is a lead to verify against the official COA, not a conclusion.** Provided as-is, no warranty.

🌿 *All prior releases are preserved; this is an additive release.*
