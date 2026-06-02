# CannaScope CT Beta V6.1 — Changelog

Refined, streamlined, crash-proof build. Older versions are preserved.

## Product classification — vapes are NEVER grouped with infused products
The cannabinoid review now uses **three strictly separate categories**:
- **Flower** — non-infused flower: whole flower, usable marijuana, shake, smalls, and **plain (non-infused) pre-rolls / joints / blunts**. → High-Cannabinoid Flower review.
- **Infused** — infused FLOWER products only: infused joints, blunts, pre-rolls, hash-holes, THCA/diamond/rosin-infused flower. → "Infused Products — Potency Reference".
- **Vapes / Concentrates / Extracts** — vape carts, disposables, pods, rosin, resin, distillate, diamonds, hash, etc. → its own "Vapes, Concentrates & Extracts — Potency Reference" (separate file + section).

Food-word strain names ("Velvet Cream", "Wedding Cake", "Mint Chocolate") are no longer mistaken for edibles/topicals — oral/topical is judged from the dosage form, not the product name.

## Anti-hallucination: per-line-item COA verification
Every flagged value must **literally appear in its COA text** (matched as a distinct number, so 0.5 is not "found" inside 0.18). Any value that doesn't is marked unverified and excluded from all findings (it falls to manual review). This is a single chokepoint that keeps an OCR/parse hallucination off the report.

## Implausible-value rejection
A measured value over 1,000× its limit, or an absurd absolute magnitude, is rejected as an OCR/parse error (e.g. a scanned COA misreading "5,088,888,888,888 CFU/g"). Genuine gross failures (a few × the limit) are kept.

## Flower potency ceiling
A "flower" cannabinoid reading above 45% (impossible for real flower) is excluded from the flower review as a parse error or mislabeled concentrate. Concentrates/extracts are uncapped.

## Crash-proof + self-pacing (handles massive runs)
- **Isolated OCR by default** — each scanned COA's OCR runs in a subprocess; a native segfault kills only that child, never the run.
- **Per-COA try/except** — no single COA (download/parse/OCR) can kill a worker.
- **Predictive overload backoff** — uses psutil (CPU+memory) or the load average to pause new OCR work when the machine is overloaded, then resume; takes its time when busy, moves fast when free.
- **OCR concurrency cap** (`--ocr-workers`, default 4) + **timeout retry** + **deferred low-load retry pass** for anything still unreadable, so no scan is permanently missed.

## Reports are never overwritten
Each report gets a unique name: `CannaScope_CT_Beta_V6_1_Report_<N>_MM_DD_YYYY.pdf`, numbered sequentially from 1 (one greater than the highest existing report in either the output or working folder) with the creation date appended.

## New flags
- `--until YYYY-MM-DD` — bound a run to a year (e.g. all of 2024).
- `--no-ocr` — force OCR off (isolated OCR is otherwise the default).
- `--ocr-workers N` — max concurrent OCR subprocesses (overload guard).
