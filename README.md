# CannaScope CT — Version 3 Beta

**A consumer-awareness tool for Connecticut cannabis.** CannaScope CT pulls
Connecticut's public cannabis product registry, opens **every** product's lab
Certificate of Analysis (COA), extracts the full contaminant panel, and produces
a clear, severity-sorted PDF that shows how close each product is to the limits —
with a **clickable link to every source COA** so you can verify each result
yourself.

> Every flag is a **lead to verify against the source COA**, never a conclusion.
> Nothing about any lab's or producer's conduct is asserted.

---

## Which file do I download?

| Your computer | Download | Then |
|---|---|---|
| **Windows** | `CannaScope-CT-V3-windows.zip` | unzip, double-click **Run CannaScope CT.bat** |
| **macOS** | `CannaScope-CT-V3-macos.zip` | unzip, right-click **Run CannaScope CT.command** → Open |
| **Linux** | `CannaScope-CT-V3-linux.zip` | unzip, run **./run.sh** |

The launcher installs everything on first run. **Requires Python 3.9+** and an
internet connection. Each run writes a **new numbered report**
(`CannaScope CT - Flagged Products - N.pdf`) to the folder so prior reports are
never overwritten.

---

## Two standards: CT legal limit vs. the CannaScope CT limit

Connecticut law sets the **CT legal limit** (the point at which a product fails).
CannaScope adds a stricter **CannaScope CT limit** — a higher, more cautious bar
than the state requires — so you can see risk *before* a product would legally
fail.

| Contaminant | CT legal limit | CannaScope CT limit (default) |
|---|---|---|
| Total yeast & mold | 100,000 CFU/g | **10,000 CFU/g** |
| Total aerobic bacteria | 100,000 CFU/g | **10,000 CFU/g** |
| Pathogens (E. coli, STEC, Salmonella, Listeria, pathogenic Aspergillus) | not detected (zero tolerance) | zero tolerance |
| Mycotoxins (aflatoxins, ochratoxin A) | < 20 µg/kg | < 20 µg/kg |
| Heavy metals / pesticides / residual solvents | per CT action levels | per CT action levels |

Every contaminant row shows **% of CT Legal Limit** *and* **% of CannaScope CT
Limit**, color-coded by proximity (≥90% dark red, 75–89.9% orange, 50–74.9%
yellow). A product can be far over the CannaScope CT limit while still legally
**passing** in Connecticut — that gap is exactly what this tool surfaces.

The CannaScope yeast/mold & aerobic limit is adjustable with `--threshold`
(default 10,000). You can set stricter personal limits for other contaminants in
`CANNASCOPE_LIMITS` inside `cannascope_ct_v3.py`.

---

## What V3 does

- **All products, all producers, all labs.** Evaluates every product type (flower,
  vapes, concentrates, edibles, tinctures, topicals) from every Connecticut
  producer, tested by any CT lab — with a per-run **coverage audit** so nothing
  is silently dropped.
- **% of Limit columns** — proximity to both the CT legal limit and the
  CannaScope CT limit, for every contaminant that has a limit.
- **Executive Summary page** — "Products Closest to the Limits," ranked by how
  near the nearest contaminant is to its limit.
- **Recognizable names** — shows each producer's common / DBA name alongside the
  legal LLC (e.g. *Fine Fettle (FFD 149 LLC)*, *Theraplant (DXR Finance 3,
  LLC)*), plus the product's brand from the COA. Lab names are normalized too.
- **Reads scanned/image-only COAs** via OCR (Apple Vision on macOS, Tesseract
  elsewhere).
- **Reads Northeast Laboratories' columnar COAs** (yeast/mold & aerobic counts
  that earlier versions could not extract).
- **Severity-sorted** report (RED → ORANGE → YELLOW), most severe first, with
  clickable COA links and a self-cleaning cache.
- **Per-Lab Analysis Summary** so you can confirm every lab's COAs were parsed.

### What RED / ORANGE / YELLOW mean
- **RED = do not consume** — a prohibited detection, an over-CT-limit result, or
  a failed pesticide/solvent panel.
- **ORANGE = high caution if sensitive.**
- **YELLOW = moderate caution** — exceeds the stricter CannaScope CT limit but
  remains LEGAL in Connecticut.

---

## Output (in the folder you run it from)

| File | What it is |
|---|---|
| `CannaScope CT - Flagged Products - N.pdf` | the numbered, color-coded report (new each run) |
| `CannaScope CT - Flagged Product Results and Sources/` | full data, source COAs, and supporting CSVs |
| `All Products Scanned - Full Results.csv` | every analyte value parsed, per product |
| `Per-Lab Analysis Summary.csv` | per-lab scanned / parsed / flagged counts |
| `Name Coverage Audit.csv` | producers & labs accounted for this run |
| `Unreadable COAs - Manual Review.csv` | COAs that could not be read even with OCR |

---

## Typical use

```bash
python cannascope_ct_v3.py                 # last 60 days, all product types (default)
python cannascope_ct_v3.py --days 180      # wider window (captures more labs/products)
python cannascope_ct_v3.py --forms flower --days 30 --limit 50   # quick test
python cannascope_ct_v3.py --threshold 5000                      # stricter CannaScope limit
```

> **macOS "can't be opened" / Windows "protected your PC"?** Normal block of a
> downloaded script. macOS: right-click the launcher → Open → Open (or `xattr
> -cr` the folder in Terminal). Windows: More info → Run anyway.

---

## Please cross-check, and report errors

Every flag is a lead to verify against the source COA — click the COA number in
any row to open the official COA and confirm. Found a misread? Please report it:
https://github.com/jmlschlee/Connecticut-Cannabis-Contaminant-Checker-Beta-V1/issues

Earlier versions remain available: **V2** under the `v0.2.0` release and the
original **Beta V1** under `v0.1.0-beta`.

*Standards encoded: Conn. Agencies Regs. §21a-408-60; DCP policy. Source data: CT
Open Data registry `egd5-wb6r`.*
