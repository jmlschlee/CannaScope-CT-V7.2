# 🌿 CannaScope CT

**Source-verified transparency reports for Connecticut cannabis — built so every number can be traced back to the product's own Certificate of Analysis (COA).**

🔗 **Live web app:** [cannascope-ct.streamlit.app](https://cannascope-ct.streamlit.app) &nbsp;·&nbsp; 💻 **Desktop download:** see [Releases](../../releases) &nbsp;·&nbsp; **Current version: V17.1.1**

---

## 🆕 What's new in V17.1.1

This release sharpens **honesty** (you can always tell whether a report was actually verified live), adds a **statistical boundary-clustering screen**, and makes the report **much easier to read**.

- 🛰️ **Honest live-verification coverage (gate, not just a counter).** Every report now states, on the cover, how many products were **re-verified against their live source COA this run**. If a run did **zero** live verification (offline, or everything served from cache), the cover is unmistakably stamped **`CACHE-REPLAY — NOT LIVE-VERIFIED THIS RUN`** and no finding is presented as live-verified — incidental OCR can no longer disguise a cache replay as a validated run. *(Earlier builds could show "0% live" while still reading as validated; that's fixed at the root — genuine live reads are now correctly credited.)*
- ⚡ **`--live-verify` switch.** Forces a fresh re-fetch of **every** COA from its source link this run (plus a full cache self-audit), so a normal online run produces real, non-zero live coverage. The run log states `LIVE VERIFICATION: ON / OFF` in one plain line.
- 📈 **New section — "Convenient Lab Result Groupings by Producer and Lab."** A statistical screen that flags **statistically unusual clustering of results just *below* a pass/fail limit**, grouped by producer + lab + analyte (primary target: yeast & mold near the limit). Each group gets a binomial p-value, z-score, chi-square goodness-of-fit, Fisher exact (small samples), a cliff-effect check, and a transparent **Convenience Score (0–100)**. It is a **review signal only — never a fraud claim** (boundary clustering can come from legitimate retests, remediation, sampling, rounding, reporting, or selection effects).
- 🏷️ **Renamed for accuracy.** "Potency Parser Conflicts" / "Impossible Cannabinoid Math" → **"Laboratory Data Consistency Flags"** (data-integrity alerts about a COA's own numbers, **not** software errors). The high-THC section is now **"Biologically Implausible High THC Flower Review."**
- 📊 **Coverage Integrity Summary** — a standing table of COAs expected / acquired / parsed / live-verified with reconciling ratios (fails loud if a denominator is zero or the buckets don't reconcile).
- 🧹 **Cleaner, more readable report (Report #-tested):** a **decluttered cover** (status, headline counts, one warning, one pointer — full detail moved to the appendix); **centered, larger** "Most Important Findings," "Statewide Snapshot," and "How To Read" blocks; a **ranked, tier-banded** "Flagged Findings by Producer" table (Highest priority ≥ 20% · Moderate 10–20% · Low < 10%, with the rule printed); pathogen findings sorted **newest → oldest**; and section headers that **never orphan** from their tables.
- 🔤 **Unicode-clean rendering** — `µg/kg` and other glyphs render correctly in every PDF viewer (an embedded Unicode font; no more "g/kg" drops or missing-glyph boxes).

> No measurement, threshold, limit, or finding was changed in V17.1.x — these are **honesty, presentation, and added-analysis** improvements.

---

## ⚖️ Please read first — what this tool is (and isn't)

CannaScope CT is an **independent, informational transparency tool**. It reads Connecticut's **public** product registry and each product's **publicly linked** lab Certificate of Analysis (COA), and organizes what those documents say into a readable report.

- ℹ️ **It is not medical, legal, or professional advice**, and it is **not affiliated with, endorsed by, or operated by** the State of Connecticut or any laboratory or producer.
- 🔎 **Every result is a lead to verify — not a conclusion.** CannaScope does **not** assert that any product is unsafe, adulterated, mislabeled, non-compliant, or fraudulent. A flag means "this is worth checking against the official COA," nothing more.
- ✅ **A value is shown only if it appears in that product's own linked COA.** Anything that can't be confidently matched to the correct product is **routed to manual review, not published.**
- 📅 Standards and limits change over time; the report shows the standard it applied and its source. **Always confirm against the official, current COA and the applicable Connecticut rule before relying on anything.**

If you are making a health, legal, or compliance decision, verify independently with the official documents and a qualified professional.

---

## ✨ What it does — full feature list

### 📋 Two ways to use it
- 🔎 **Look up a product** — search by product or brand name (or enter a batch / COA number / UID) and get a plain-English PDF review of that product and its lab results.
- 🏛️ **Statewide transparency report** — review every product registered in a date window you choose, as one downloadable PDF.

### 🧪 What it reads from each COA
- 🦠 **Microbials** — total yeast & mold, total aerobic bacteria, and pathogen screens (Salmonella, E. coli, etc.)
- ⚗️ **Heavy metals** — arsenic, cadmium, lead, mercury, chromium
- 🌾 **Pesticides** and 🧴 **residual solvents**
- 🍞 **Mycotoxins** (aflatoxins / ochratoxin)
- 🌿 **Cannabinoids / potency** — THC, CBD, and totals (Total THC computed from the COA's own components, never an inflated stated figure)
- ✅ / ❌ **Pass / fail status** as printed on the COA

### 🛡️ How it protects accuracy
- 🔗 **Source verification** — every published value is re-checked against the product's own linked COA before it appears.
- 🛰️ **Live-first, live always wins** — the cache is only a speed hint, never trusted blindly. Online runs re-pull the live COA and **correct the cache when they disagree**; runs honestly report how much was verified live this run, and a no-live-verification run is stamped **CACHE-REPLAY — NOT LIVE-VERIFIED**.
- ⚡ **`--live-verify`** forces a fresh live re-fetch of every COA for a fully live-verified report.
- 🧬 **Multi-product COA handling** — some COA PDFs contain several products. CannaScope isolates **each product's own block** and will **never** attribute one product's results to another; if it can't be sure, it routes the record to review instead of guessing.
- 📅 **Date-window integrity** — a statewide report contains **only** records whose COA test date falls inside the requested window; the run shows the exact window applied and **stops rather than publish** anything outside it.
- 🔬 **Reads 5×, never guesses** — image-only COAs are OCR'd up to **5 escalating attempts**; a value is left "unable to read" only after honest retries — a confidently-wrong safety number is never emitted.
- 🧯 **Conservative by design** — when extraction is uncertain, the value is **held for manual review**, not published.
- 🧫 **Below-detection aware** — "less-than" detection limits (e.g. `<10,000 CFU/g`) are treated as bounds, not failing measurements.
- 🚦 **Fail-loud guarantees** — out-of-window data, an empty report, or a non-reconciling accounting bucket **stop the run** rather than publish something misleading.
- 🖥️ **Cross-platform** — identical behavior on macOS, Windows, and Linux.

### 📚 Regulatory context & analysis
- 📜 **Per-year Connecticut standards (2015–2026)** with citations, plus a live re-consult of public CT sources, so each result is judged against the limit that applied at its test date.
- 🏛️ **Patient-safety / ombudsman review** highlighting near-limit results for medical patients.
- 🔁 **Conflicting-COA detection** — flags when a product has multiple or differing COAs (e.g. a retest), shown side-by-side for comparison.
- 📊 **Producer & lab summaries** — honest, comparable rates (a producer's flagged products ÷ that producer's total in the window), now **ranked and tier-banded**.
- 📈 **Convenient Lab Result Groupings** — the statistical boundary-clustering screen (binomial / z-score / chi-square / Fisher exact / cliff-effect / 0–100 Convenience Score), with a public summary and a full statistical appendix. **Warrants review — never proof of intent.**
- 🧮 **Laboratory Data Consistency Flags** — surfaces internally inconsistent COA numbers (e.g. Total THC > Total Cannabinoids) as **data-integrity alerts**, held out of findings for manual re-read.
- 🌿 **Biologically Implausible High THC Flower Review** — non-infused flower with verified Total THC above 35% (implausible for dry flower), a label-accuracy review signal.

### 📦 Outputs, transparency & performance
- 🧾 **Downloadable PDF** report you can save, print, or share, plus 📑 **CSV exports** for every section and a transparent debug log.
- 🧰 **Technical Validation & Diagnostics appendix** — Coverage Integrity Summary, validation counters, date-window integrity, source-binding audit, self-audit, parser/OCR diagnostics, and definitions (kept out of the consumer-facing pages).
- 💾 **Triple-verified COA data cache** — COAs are read once and reused, so reports build quickly and can run **offline** from the bundled dataset (clearly labeled as a cache replay).
- 🖼️ **OCR** for older scanned / image-only COAs.
- 🔢 **Provenance & audit trail** — report numbering, source URLs, and a per-value verification stamp.

---

## 🚀 Getting started

**Web (easiest):** open [cannascope-ct.streamlit.app](https://cannascope-ct.streamlit.app), pick a mode, choose your window or search a product, and click **Generate the PDF report**.

**Desktop:** download the package for your OS from [Releases](../../releases), unzip, and run the included `run_statewide_report` / `run_consumer_concern_report` script (Python 3.9+; `pip install -r requirements.txt`).

```bash
# Statewide report (live-first; add --live-verify to force a fully live re-verified run)
python CannaScope_CT_V17.py statewide --since 2024-01-01 --until 2024-12-31
python CannaScope_CT_V17.py statewide --since 2024-01-01 --until 2024-12-31 --live-verify

# Single-product consumer report
python CannaScope_CT_V17.py concern --example
```

---

## 🗂️ Data sources
Connecticut public product registry (data.ct.gov) + each product's publicly linked Certificate of Analysis. CannaScope stores and reuses what those public documents say; it does not generate lab results.

## 📄 License
See [LICENSE](LICENSE). Provided **as-is, for informational and transparency purposes only, with no warranty**.

*CannaScope CT surfaces what the public record says so patients, caregivers, and professionals can verify it themselves — quickly, and against the source.* 🌿
