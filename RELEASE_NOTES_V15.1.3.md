# CannaScope CT V15.1.3 🌿

**An additive report-quality patch on top of V15.1.2.** Every prior release stays live and
unchanged — nothing was deleted or renamed. This release fixes table rendering, removes an accuracy
contradiction in the legal-standard table, and documents coverage gaps more honestly.

## 🔧 What's fixed

- **📅 Dates never wrap or split mid-value.** In every table, a testing date is now an atomic,
  non-breaking token sized to fit a full `YYYY-MM-DD` — no more `2025-07-0` + `2` on two lines.
- **🏷️ Status words never break.** The Legal Standard Verification table no longer splits
  `UNVERIFIED` into `UNVERIFIE` + `D`.
- **🔢 Value + unit stay together.** In the Yeast & Mold review, a number and its unit no longer
  split (`380,000 CFU/g`, `not disclosed`).
- **⚖️ The Legal Standard Verification table now matches what the program actually did.** It used to
  mark categories like yeast & mold "UNVERIFIED" even though the report applied a known dated CT limit
  (e.g. **100,000 CFU/g**) to judge those rows. The table now shows the **applied dated standard** it
  used in one column and a **separate, clearly-worded live-confirmation status** in another. The bare
  "not verified — manual legal review needed" wording is reserved for categories/eras with genuinely
  no dated value on record.

## ✨ Also improved

- **🧾 Conflicting-COA section is shorter and clearer.** The shared caveat that repeated on every one
  of ~75 leads is now stated once at the top; each case keeps only its own specifics.
- **🔍 Higher-quality OCR for image-only COAs.** A scanned COA whose first OCR pass returns no text is
  re-rendered at a higher resolution and re-OCR'd (an escalating-DPI retry). Clean COAs are unaffected.
- **📝 More honest coverage-gap wording.** Unreadable COAs are now described as unreadable "even after
  an escalating-DPI OCR retry," documenting what was attempted before a record is held out as a gap.

## ✅ Unchanged

Every V15.1.2 / V15.1.1 / V15.1.0 capability is intact — the live-source fix, legal-cache versioning,
`audit-cache`, the Streamlit app, and all findings logic. No behavior changed beyond the items above.

## 📦 Downloads

Self-contained, single-file builds (Python 3.9+), each with a README, installer guide, and launch
scripts:

- `CannaScopeCT-V15.1.3-Windows.zip`
- `CannaScopeCT-V15.1.3-macOS.zip`
- `CannaScopeCT-V15.1.3-Linux.zip`

> ⚖️ Advisory research tool — **not** legal, medical, or professional advice, and **not** affiliated
> with the State of Connecticut. Every flag is a **lead to verify, not a conclusion.**
