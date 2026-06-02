# CannaScope CT Beta Version 4

## ⬇️ Download — CannaScope CT Beta 4 (latest)

Pick your operating system. Each is a self-contained package (unzip and run).

| Operating system | Download |
|---|---|
| 🪟 **Windows** | **[CannaScope-CT-V4-windows.zip](https://github.com/jmlschlee/CannaScope-CT-Beta-4/releases/latest/download/CannaScope-CT-V4-windows.zip)** |
| 🍎 **macOS** | **[CannaScope-CT-V4-macos.zip](https://github.com/jmlschlee/CannaScope-CT-Beta-4/releases/latest/download/CannaScope-CT-V4-macos.zip)** |
| 🐧 **Linux** | **[CannaScope-CT-V4-linux.zip](https://github.com/jmlschlee/CannaScope-CT-Beta-4/releases/latest/download/CannaScope-CT-V4-linux.zip)** |

All builds (and older versions) are on the **[Releases page](https://github.com/jmlschlee/CannaScope-CT-Beta-4/releases)**. See **[INSTALL.md](INSTALL.md)** for step-by-step setup.

---


**A consumer-awareness tool for Connecticut cannabis.** CannaScope CT pulls
Connecticut's public cannabis product registry, opens **every** product's lab
Certificate of Analysis (COA) across **all producers and all CT labs**, extracts
the full contaminant panel, and produces a clear, severity-sorted PDF that shows
how close each result is to **two** thresholds — with a **clickable link to every
source COA** so you can verify each result yourself.

> Every flag is a **LEAD, not a conclusion. Verify each product against its COA.**
> Nothing about any lab's or producer's conduct is asserted.

---

## Which file do I download?

| Your computer | Download | Then |
|---|---|---|
| **Windows** | `CannaScope-CT-V4-windows.zip` | unzip, double-click **Run CannaScope CT.bat** |
| **macOS** | `CannaScope-CT-V4-macos.zip` | unzip, right-click **Run CannaScope CT.command** → Open |
| **Linux** | `CannaScope-CT-V4-linux.zip` | unzip, run **./run.sh** |

The launcher installs everything on first run. **Requires Python 3.9+** and an
internet connection. Each run writes a **new numbered report**
(`CannaScope CT Beta Version 4 - Flagged Products - N.pdf`) so prior reports are
never overwritten, and also drops a copy at the top of the run folder.

See **INSTALL.md** for detailed per-OS instructions.

---

## Two thresholds: Connecticut Legal Limit vs. CannaScope CT Standard

Connecticut law sets the **Connecticut Legal Limit** (where a product fails).
CannaScope adds a stricter **CannaScope CT Standard** so you can see risk *before*
a product would legally fail.

> **CannaScope CT Standard is a stricter consumer-awareness threshold. It is not a
> Connecticut legal failure standard.** Exceeding it is **not** illegal.

| Contaminant | Connecticut Legal Limit | CannaScope CT Standard |
|---|---|---|
| Total Yeast & Mold | 100,000 CFU/g | **10,000 CFU/g** |
| Total Aerobic Bacteria | 100,000 CFU/g | **10,000 CFU/g** |
| Heavy Metals, Mycotoxins, Pesticides, other regulated contaminants | per CT action level | **50% of the Connecticut Legal Limit** |

Examples (50% rule): Arsenic 200 → **100** µg/kg · Lead 500 → **250** µg/kg ·
Chromium 600 → **300** µg/kg · Cadmium 1,500 → **750** µg/kg.

Each contaminant row shows:

- **CT Limit %** = Measured Value ÷ Connecticut Legal Limit × 100 — e.g.
  `91.7% of CT Limit`.
- **vs CannaScope CT Standard** = (Measured Value − CannaScope CT Standard) ÷
  CannaScope CT Standard × 100 — e.g. `+83.4% Over CannaScope CT Standard`,
  `0% At CannaScope CT Standard`, or `-20.0% Below CannaScope CT Standard`.

The yeast/mold & aerobic CannaScope CT Standard is adjustable with `--threshold`
(default 10,000).

---

## What Version 4 adds

- **CannaScope CT Standard** reported alongside the **Connecticut Legal Limit**,
  with the two clear columns above.
- **Executive Summary** with five sections: Products Closest to Connecticut Legal
  Limits, Products Furthest Above CannaScope CT Standard, Top Producers by Flag
  Count, Top Contaminants Detected, and Most Frequently Flagged Labs.
- **Date Created** and **Time Created** on every report (header + footer).
- **Cleaner typography** — cross-platform font, larger text, better spacing,
  consistent capitalization, COA links blue/underlined/clickable, and the
  disclaimer on every page.

Carried over from earlier versions: all product types, recognizable producer
DBA + legal names, normalized lab names, OCR for scanned COAs, Northeast
Laboratories columnar parsing, per-lab analysis summary, and a name coverage
audit so every lab and producer is accounted for.

### What RED / ORANGE / YELLOW mean
- **RED = Do Not Consume** — a prohibited detection, an over-Connecticut-Legal-Limit
  result, or a failed pesticide/solvent panel.
- **ORANGE = High Caution** if sensitive.
- **YELLOW = Moderate Caution** — exceeds the stricter CannaScope CT Standard but
  remains LEGAL in Connecticut.

---

## Typical use

```bash
python cannascope_ct_v4.py                 # last 60 days, all product types (default)
python cannascope_ct_v4.py --days 180      # wider window (more labs/products)
python cannascope_ct_v4.py --threshold 5000   # stricter CannaScope CT Standard for yeast/mold & aerobic
```

> **macOS "can't be opened" / Windows "protected your PC"?** Normal block of a
> downloaded script. macOS: right-click the launcher → Open → Open. Windows: More
> info → Run anyway.

---

## Please cross-check, and report errors

Every flag is a LEAD to verify against the source COA — click the COA number in
any row to open the official COA and confirm. Found a misread? Please report it:
https://github.com/jmlschlee/CannaScope-CT-Beta-4/issues

Earlier versions remain available, unchanged: **V3** (`v0.3.0`), **V2**
(`v0.2.0`), and the original **Beta V1** (`v0.1.0-beta`).

*Standards encoded: Conn. Agencies Regs. §21a-408-60; DCP policy. Source data: CT
Open Data registry `egd5-wb6r`.*
