# 🌿 CannaScope CT V14 — full release

**Connecticut Cannabis Transparency Report — source-verified consumer-awareness & testing-pattern review.**

CannaScope CT reads Connecticut's **public** cannabis product registry, pulls each product's **live Certificate of Analysis (COA)**, checks it carefully, and turns it into clear, source-verified PDF reports. *Every flag is a lead, not a conclusion — always verify against the live COA. Not legal or medical advice.*

V14 carries **everything** from V13 and adds three things on top. All previous releases stay live and unchanged — **nothing was removed.**

---

## ⬇️ Downloads — pick your operating system

| OS | Download | Launch |
|---|---|---|
| 🪟 **Windows** | **CannaScope CT V14 - Windows.zip** | unzip → `run.bat statewide --days 90` |
| 🍎 **macOS** | **CannaScope CT V14 - macOS.zip** | unzip → `chmod +x run.sh && ./run.sh statewide --days 90` |
| 🐧 **Linux** | **CannaScope CT V14 - Linux.zip** | unzip → `chmod +x run.sh && ./run.sh statewide --days 90` |

Each download is **one self-contained file** (`CannaScope_CT_V14.py`) plus a one-click launcher, quick-start guide, and license. No companion files, no build step — just Python 3.9+.

---

## 🔁 What changed between V13 and V14

V13 was already a big readability + integrity + feature release. V14 makes the parser **smarter about old/odd lab reports**, gives every report a **clean, permanent, uniquely-numbered filename**, and tidies the page layout.

### 🆕 Added in V14

- 🧠 **COA Format Learning Layer (historical, year-by-year awareness).**
  Connecticut's lab reports have changed shape many times since 2015 — different labs, different templates, sections in different orders, different wording for "pass," "fail," and "not detected," and lots of older scanned/image PDFs. V14 no longer assumes one fixed format. For each COA it:
  1. **Figures out the format** — which lab, which year/era, which sections are present and in what order, and the pass/fail wording used.
  2. **Double-checks itself five ways** instead of trusting one read: the top-level pass/fail summary, the detailed result tables, the actual numbers, the batch/product/licensee identity, and whether the COA truly matches the product it's attached to.
  3. **Holds back anything that looks wrong** — if a report says "PASS" up top but a detailed result fails, or the numbers are impossible, or the COA doesn't match the product, the result is marked **UNCERTAIN and kept out of the report** (sent to a review list) instead of being published as fact.
  4. **Builds a per-year readiness map** that grows every run, so the program knows which years it can read confidently.
  - New **`learn`** command runs a self-test across every year and prints a parsing-confidence report (year · COAs sampled · labs/producers seen · fields read · uncertain count · known layout patterns · **ready for reports? yes/no**):
    ```
    python3 CannaScope_CT_V14.py learn --years 2015-2026
    ```
  - The statewide report gains a **"COA Format Learning & Extraction Confidence"** appendix and two new CSVs.

- 🗂️ **New PDF report naming standard + one global report number.**
  Every report now saves with a clean, instantly-identifiable name:
  ```
  [REPORT#]-CannaScopeCT-V[VERSION]-[TYPE]-[DATE]-[TIME].pdf
  15-CannaScopeCT-V14-Statewide-2026-6-4-5:36PM.pdf
  16-CannaScopeCT-V14-ConsumerConcern-2026-6-4-9:49PM.pdf
  ```
  The **report number is global and continuous across both report types** (Statewide and ConsumerConcern share one ever-increasing counter), it **never resets**, and reports are **never overwritten, renamed, or deleted** — every run is a brand-new file, building a permanent archive. The cover page matches: program name, `Report #N`, report type, "Created June 4, 2026," and the time.
  *(Note for macOS users: the Finder shows the `:` in the time as `/`; Terminal shows it correctly.)*

- 📄 **Cleaner pages + easier-to-read tables.**
  - **Adaptive white-space reflow** — long tables now flow naturally and fill each page, instead of jumping to the next page and leaving big gaps. Works on both large and small reports.
  - **Right-aligned number columns** (with matching headers) so measured values, limits, and percentages line up and are easy to scan.

- 🔁 **Lab-shopping checks now remember across runs.**
  The "Conflicting COA Results & Possible Lab-Shopping Indicators" review now keeps a persistent record between runs, so a conflict whose two lab reports were scanned on **different days** is still caught, and earlier findings aren't lost on a re-run. (Still neutral and human-review-only — never an accusation.)

### ✅ Unchanged from V13
The detection engine, the Connecticut limits/calculations, and the core integrity rule (a value is published only if it literally appears in that product's own COA) are unchanged. The heavy single-file build ships inside the download zips; the embedded registry snapshot is intentionally not committed to git to keep the repository small.

---

## 📋 What this program does (plain-language overview)

CannaScope CT is **two reports in one program**, plus a self-check:

- 🗺️ **Statewide Transparency Report** (`statewide`) — scans the whole Connecticut market over any date range and shows the patterns worth a closer look.
- 🔎 **Personalized Product Concern Report** (`concern`) — a careful, advisory review of **one product** a consumer is worried about, found from whatever they have (name, batch, NDC, UID/lot, COA number, dates, or a QR link). Advisory only — **not medical advice.**
- 🧠 **COA Format Learning self-test** (`learn`) — practices reading historical COAs year by year and reports how confidently it can read each year.

What it checks and shows:

- 🧪 **Every mandated contaminant panel** — yeast & mold, total aerobic bacteria, heavy metals (arsenic, cadmium, chromium, lead, mercury), mycotoxins, residual solvents, and zero-tolerance pathogens — each ranked by how close it is to the Connecticut legal limit.
- 🧫 **Year- and lab-aware mold limits** — Connecticut's passing limit for yeast & mold changed over the years (by up to 100×) and differed between labs; each result is shown against the limit that actually applied, the current limit, and a strict patient-protective benchmark.
- 🌾 **High-cannabinoid review** — flags unusually high THC flower with a full breakdown (THCA · Δ9-THC · CBD · Total THC · Total Cannabinoids), and ignores impossible readings as parse errors.
- ⚖️ **Conflicting COA / possible lab-shopping** — neutrally surfaces, for human review, when the same physical lot shows conflicting pass/fail results across labs (now remembered across runs). Never an accusation.
- 🛡️ **Anti-bad-data protections** — every published number must be found in the product's own COA, the new format-learning layer holds back anything uncertain, and the report honestly labels itself `PASS` / `PASS WITH WARNINGS` / `DRAFT` / `FAIL`.
- 🩺 **Patient-safety & compliance leads** — a "closest to a contaminant limit" review for the CT Cannabis Ombudsman, and cautious compliance review leads — all human-review-only, never legal determinations.
- 🏷️ **Producer / brand identity** with a 0–100 confidence score, checked against public Connecticut records.
- 📅 **Any time window** — a single quarter up to the full **2015–2026** registry (~33,000 products).
- 🖨️ **Reads scanned/image COAs** with crash-proof OCR that slows itself down before a big run can run out of memory, so no document is skipped.
- 📦 **Offline mode** — cache everything once with `--keep-clean-pdfs`, then re-run with `--offline`, no internet needed.
- 🧾 **A permanent archive** — every report is uniquely numbered and never overwritten.

---

## 🚀 Quick start

```bash
# any OS, Python 3.9+
python3 -m pip install -r requirements.txt

# whole-market report for a date range
python3 CannaScope_CT_V14.py statewide --since 2024-01-01 --until 2024-12-31

# one product a consumer is worried about
python3 CannaScope_CT_V14.py concern --example

# how well can it read each year's COAs?
python3 CannaScope_CT_V14.py learn --years 2015-2026
```

Or use the bundled launcher for your OS (`run.sh` / `run.bat`).

---

## ⚖️ Disclaimer

CannaScope CT is a **consumer-awareness research tool** — not legal, medical, or professional advice, and not affiliated with the State of Connecticut. Findings are leads to verify, not conclusions or accusations. Always confirm against the official, live COA.
