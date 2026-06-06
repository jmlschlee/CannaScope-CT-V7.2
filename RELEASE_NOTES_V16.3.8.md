# CannaScope CT V16.3.8

**Date-window integrity + an independent, live, end-to-end verification of the dataset.** This release
strengthens the guarantees behind every statewide report and updates the hosted web app. As always,
CannaScope is an informational transparency tool — results are **leads to verify against the official
COA, not conclusions**, and it is **not** medical, legal, or professional advice and **not** affiliated
with the State of Connecticut.

## 📅 Date-window integrity (new)
A statewide report now contains **only** records whose **COA test date** falls inside the exact requested
reporting window — so every finding, statistic, ranking, and trend is generated solely from in-window
records.
- Enforced at a single chokepoint on the COA test date (the date that matters for review), applied
  identically to freshly-read and cache-reloaded records, so no cached, historical, merged, or
  section-level path can introduce out-of-window data.
- Records whose COA test date is outside the window — or that have no confirmable test date — are
  **excluded and counted**, never analyzed.
- **Hard validation + publication safety:** before a report is produced, the minimum and maximum COA test
  dates of the final dataset are checked against the requested window. If anything falls outside, the run
  **stops with a "DATE INTEGRITY" error instead of publishing** a potentially misleading report.
- A new **Date-Window Integrity** section in the report (and the debug log) shows the requested window,
  the actual dataset window, and how many records were included vs. excluded by date.
- Verified by an automated regression across single-year and multi-year windows (2015 → 2026).

## 🔎 Independent end-to-end data verification
We re-read **every value-carrying 2015–2026 record (15,803)** directly against its source COA — **live
web-pulling 9,461 COAs fresh** rather than trusting the cache — and independently checked, for any COA
that contains more than one product, that each value belongs to **that product's own block**.
- **No cross-attribution was found** (a value being shown under the wrong product): **0 of 15,803**.
- A small number of older COAs simply don't print the registry brand name (they use lot/strain codes);
  those values were confirmed present in the correct COA and are handled conservatively.

## 🎨 Hosted web app
- Pinned a **light theme and forced high-contrast dark text** so the app renders correctly regardless of
  the visitor's browser/OS dark-mode setting (fixes washed-out / low-contrast text and form controls).
- The version badge reads the **actual** program version automatically.
- Cache-backed report modes run **offline** on the hosting tier for speed and reliability.

## 🗂️ Notes
- The bundled, triple-verified COA dataset is refreshed and embedded for fast offline reports.
- Additive release — all prior releases remain available. `ANALYSIS_VERSION` → 16.3.8.

**Reminder:** always confirm any result against the product's official, current Certificate of Analysis
and the applicable Connecticut rule before relying on it.
