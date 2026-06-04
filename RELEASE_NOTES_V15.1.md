# CannaScope CT V15.1

An **additive maintenance + deployability** release on top of V15.0.0. V15.0.0 and every prior
beta stay live and unchanged — V15.1 is added alongside them.

## 🆕 What V15.1 adds
- 🔁 **Pre-V16 cache audit (`audit-cache`)** — re-validates the scan ledger against the current
  analysis-logic version: re-evaluates previously clean-skipped records under current
  detection/validation, surfaces any that now produce findings, and re-stamps the cache as current.
  Resumable, batched, checkpointed, non-destructive (backs up the ledger first). A full local run
  re-checked ~17k records and confirmed the stale cache was **not** hiding findings.
- 🧪 **`--force-rescan`** (on `audit-cache` and `statewide`) — ignore the skip-list and reprocess
  everything from scratch, for testing / validation / dev.
- 🌐 **Streamlit web app (`streamlit_app.py`)** — a friendly browser UI with two modes (Statewide
  sample · Consumer Concern lookup) that drives the V15 program and serves the PDF via a download
  button. Deployable on Streamlit Community Cloud from `main`; light work per click; `st.secrets` only.
- 🗂️ **Tidier output** — each per-run report folder now keeps all CSV + diagnostic exports in a
  **`Data Exports`** subfolder, leaving just the PDF + that subfolder at the top.
- Declared version bumped to **15.1** (cover / footer / metadata).

## ✅ Everything from V15.0.0 (unchanged)
Source-verified statewide + consumer reports; the COA integrity rule (a value is published only if
it appears in its own linked COA) + six-field triple-check; date- & lab-aware Yeast & Mold review;
three-part potency review (High THC Flower / Impossible Math / Product-Type Misclassification);
recomputed, consistency-gated conflict math with correct same-lab vs cross-lab wording; the CT
Cannabis Ombudsman patient-safety review and triaged compliance leads (both with testing dates);
legal date-aware standard verification (local-first, internet-fallback, fail-safe, never fabricated);
Coverage Gaps / Unvalidated COAs; Software Self-Enhancement & Self-Audit + persistent improvement
log; year-by-year COA format learning; short PDF filenames + per-run folders + persistent numbering
registry. Full detail stays inside each PDF.

## 📦 Download options
- `CannaScopeCT-V15.1-Windows.zip` — incl. `run_statewide_report.bat`, `run_consumer_concern_report.bat`
- `CannaScopeCT-V15.1-macOS.zip` — incl. `run_statewide_report.command`, `run_consumer_concern_report.command`
- `CannaScopeCT-V15.1-Linux.zip` — incl. `run_statewide_report.sh`, `run_consumer_concern_report.sh`

Each package is the single self-contained `CannaScope_CT_V15.py` (engine + cannabinoid/identity
layer + name resolver + OCR worker embedded) plus README, requirements, LICENSE, and INSTALL.
Requires Python 3.9+ and the listed libraries. **Web users** don't need a download — deploy the
repo on Streamlit Community Cloud (branch `main`, main file `streamlit_app.py`).

## ⚖️ Advisory
A consumer-awareness research tool — not legal, medical, or professional advice, and not affiliated
with the State of Connecticut. Findings are leads to verify, not conclusions. Always confirm against
the official, live COA.
