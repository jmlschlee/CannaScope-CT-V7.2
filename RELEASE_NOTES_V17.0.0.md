# CannaScope CT V17.0.0

Connecticut cannabis COA testing & transparency reporting — a major reliability release. The headline
change: **the cache is now treated as a hint, never the source of truth — the live COA at its source link
is always the authority**, and the program proves it on every run.

## Headline — SUPERIOR RULE: active cache self-audit (cache is a hint, live is the authority)
Every online, cache-backed run now PROACTIVELY spot-checks the cache against live data before trusting it:
- A representative, deterministic (stride-sampled) set of cached COAs is **re-pulled LIVE** from its source
  link and compared to the cache.
- **Live always wins:** any disagreeing row is corrected to the live value; the audit **widens** when the
  first pass disagrees; a genuine **value conflict distrusts the cache for the whole window** and forces a
  full live re-pull.
- A now-dead / unreadable live re-pull is never counted as a false disagreement.
- **Offline runs disclose "cache UNVERIFIED this run"** instead of silently trusting.
- Flags: `--cache-audit-sample N` (default 15), `--full-cache-audit`, `--no-cache-audit`.

## Cross-platform acceptance criteria (every run, every OS: macOS / Windows / Linux)
- **Cross-platform OCR & process handling** — Apple Vision (ocrmac) on macOS, Tesseract on Windows/Linux;
  the OCR subprocess launches in its own process group on every OS (POSIX `start_new_session` /
  Windows `CREATE_NEW_PROCESS_GROUP`).
- **When in doubt, go live** — an empty OR garbled/implausible cached row is re-pulled live and re-read.
- **OCR retried up to 5×** with an escalating render-DPI ladder; a field is left "unable to read" only after
  5 honest attempts — never fabricated.
- **Triple-check every step** — a physical units/ranges plausibility cross-check gates any implausible value
  OUT of publication; the date stage hard-validates; the render stage guards against blank output.
- **An empty report is a hard failure** — if COAs exist in the window but nothing parsed and nothing
  published, the run fails loud (no silent blank).
- **Out-of-range data is a hard failure** — only records whose COA test date is inside the requested window
  are reported; any confirmable-test-date leak aborts the run.

## Also in V17 (carried + reconciled from the 16.3.x line)
- Online-OCR fallback in the report path (empty cached COAs are re-read live).
- 2015-era columnar HEAVY METALS + MYCOTOXINS parser (defensive, below-detect-aware, garble-proof).
- Persisted training ledger + `diagnose-learning` + training→report traceability.
- `--forensic-no-cache` mode, honest category-level coverage accounting, and a multi-product block-binding map.
- Validation messaging derived from the worst readiness state; evidence-gated learning recommendation
  (emits "TRAINING STAGNATION DETECTED" instead of "run learn again" when re-training cannot help).

## Verification
All test suites pass: cache-audit, OCR-escalation, plausibility, acceptance guards, columnar metals/myco,
multi-product, multi-product cache, report integrity, date-window (9 ranges), training ledger. The cache
self-audit was verified live (12/12 sampled COAs agreed) and with a real corruption demo (a faked cache
value was caught against the live source, corrected, and the cache distrusted).

Additive release — all prior releases preserved.
