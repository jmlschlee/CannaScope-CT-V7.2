# CannaScope CT V15.1.1 🌿

**An additive patch on top of V15.1.0.** Every prior release (V15.1.0, V15.0.0, and every beta)
stays live and unchanged — nothing was deleted or renamed. This release fixes the program's
ability to reach the **live Connecticut legal-reference sources** used by the by-test-date
Legal Standard Verification step.

## 🔧 What's fixed

The date-aware legal-standard verifier had stopped reaching every CT source it consults. All three
are restored:

- **🏛️ CT DCP cannabis program** — the deep link had moved (HTTP 404). Updated to the current page,
  `portal.ct.gov/cannabis/medical-marijuana-program`.
- **📜 CT eRegulations** — was timing out on a short 8-second budget. The per-source timeout is now
  **25 seconds**, with one automatic retry on a transient timeout / connection error.
- **🔐 CT General Statutes (cga.ct.gov)** — the state server presents an *incomplete* TLS certificate
  chain (it omits the GoDaddy intermediate), so verification failed with *"unable to get local issuer
  certificate."* CannaScope now supplies that well-known intermediate and verifies against it, so the
  chain validates **with TLS certificate verification still on** — we complete the chain the server
  should have sent, we do **not** disable any security check.

These are read-only fetches of public CT legal pages. The verifier still **never fabricates** a dated
limit and continues to mark anything it cannot confirm as *"Historical standard not verified — manual
legal review needed."* The product-registry download (data.ct.gov) and offline mode were not affected.

## ✅ Unchanged

Every V15.1.0 capability is preserved: the `audit-cache` subcommand, the `Data Exports` subfolder,
the Streamlit web app, short PDF filenames, per-run folders, the six-field COA triple-check, and the
three-part potency review. No behavior changed beyond the live-source fetch fix above.

## 📦 Downloads

Self-contained, single-file builds (Python 3.9+). Each zip includes the program, a README, an
installer guide, and ready-to-run launch scripts:

- `CannaScopeCT-V15.1.1-Windows.zip`
- `CannaScopeCT-V15.1.1-macOS.zip`
- `CannaScopeCT-V15.1.1-Linux.zip`

> ⚖️ Advisory research tool — **not** legal, medical, or professional advice, and **not** affiliated
> with the State of Connecticut. Every flag is a **lead to verify, not a conclusion.**
