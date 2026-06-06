# CannaScope CT V16.2.2

**Conflicting-COA section, reprioritized for review.** The "Multiple / Conflicting COA Records" section
now leads with the cases a reviewer most wants to see first — records where the **reported analytical
result actually changed between COAs** — and ends with records that differ only in administrative
metadata. Conservative, non-accusatory tone is unchanged; nothing was removed.

## What changed
- **Ordered by what changed**, not by date or raw severity:
  1. **Compliance-outcome changes** first (PASS↔FAIL, DETECTED↔ND) — the most significant;
  2. **Changed analytical results** next (different value or status, same pass/fail outcome), **largest
     change first**;
  3. **Metadata-only** differences last (reported results identical; only COA reference / date differ) —
     kept for completeness.
- **Per-case tag** leads each case head, color-coded: `[RESULT CHANGED — compliance outcome]`,
  `[RESULT CHANGED]`, or `[METADATA ONLY — results identical]`.
- **A "What changed" scoreboard** at the top of the section counts each class so a reader sees the
  breakdown at a glance and knows the cases are listed result-changes-first.
- The existing per-case **"Compare:"** line (COA reference / dates / pass-fail / values identical-or-
  different) and the side-by-side table are unchanged, so the reader can still see exactly what differs.

Mechanically, each finding now carries a `change_class` (compliance_changed / result_changed /
metadata_only) and a magnitude; the detector sorts by change class → magnitude → severity. Metadata-only
records are retained, just ranked last. No detection logic or thresholds changed; `ANALYSIS_VERSION`
stays 15.1.0. Verified on a 2-year report (99 cases). All prior releases remain live.

## Downloads
`CannaScopeCT-V16.2.2-{Windows,macOS,Linux}.zip` — the self-contained `CannaScope_CT_V16.py` plus run scripts.
