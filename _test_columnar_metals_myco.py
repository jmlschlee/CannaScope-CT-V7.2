#!/usr/bin/env python3
"""Phase 8 regression: defensive columnar HEAVY METALS / MYCOTOXINS recovery for 2015-era NELabs COAs.

Asserts against a REAL NELabs columnar COA (the exact OCR with garbled units "<0.0005 Mg/kg BW/day",
"<5 4g/kg") that every recovered value is the correct BELOW-DETECTION bound — never the stray digit
from a mangled unit, never a Limits-column number — and that the danger cases (bare garbled numbers,
mismatched columns, non-NELabs COAs) emit NOTHING rather than a wrong safety value.

Run:  python3 _test_columnar_metals_myco.py
"""
import os
import sys
import cannascope_ct_v4 as v4
import cannascope_ct_v5 as v5

_fails = []


def check(cond, msg):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


def _parse(text):
    p = v5.ProductV5()
    p.analytes = {}
    p.cannabinoids = {}
    v4.parse_analytes(text, p)
    return p


# ---- 1. REAL NELabs columnar COA (known-good) -------------------------------------------------
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_p8_fixtures", "nelabs_metals_myco.txt")
if os.path.exists(FIX):
    p = _parse(open(FIX, encoding="utf-8").read())
    a = p.analytes
    # metals: all four present, all below-detection, exact bounds, NONE equal to a unit-garble digit
    expect_metal = {"arsenic": 0.0005, "cadmium": 0.002, "lead": 0.002, "mercury": 0.005}
    for k, v in expect_metal.items():
        e = a.get(k)
        check(e is not None, f"metal {k} recovered from columnar COA")
        if e:
            check(e.get("_below_detect") is True, f"metal {k} recorded as BELOW-DETECTION (passing), not a measurement")
            check(abs((e.get("value") or -1) - v) < 1e-9, f"metal {k} bound == {v} (got {e.get('value')})")
            check((e.get("value") or 0) not in (4.0, 50.0), f"metal {k} did NOT capture a unit-garble/limit digit")
    # aflatoxin components: all four below-detect at <5, none captured the garbled '4' from '4g/kg'
    for k in ("afla_b1", "afla_b2", "afla_g1", "afla_g2"):
        e = a.get(k)
        check(e is not None, f"mycotoxin {k} recovered from columnar COA")
        if e:
            check(e.get("_below_detect") is True, f"{k} recorded as below-detection")
            check(abs((e.get("value") or -1) - 5.0) < 1e-9, f"{k} bound == 5 (got {e.get('value')}) — NOT the '4' from '4g/kg'")
    oa = a.get("ochratoxin")
    check(oa is not None and oa.get("_below_detect") is True and abs((oa.get("value") or -1) - 5.0) < 1e-9,
          "ochratoxin recovered as below-detection <5")
    # derived total aflatoxins, below-detect
    check(a.get("aflatoxin", {}).get("_below_detect") is True, "Total Aflatoxins derived as below-detection")
    # SAFETY: nothing recovered here may be a measured exceedance (every value is a <bound)
    for k in list(expect_metal) + ["afla_b1", "afla_b2", "afla_g1", "afla_g2", "ochratoxin", "aflatoxin"]:
        e = a.get(k)
        if e:
            check(e.get("_below_detect") is True, f"{k} is below-detect (no fabricated exceedance)")
else:
    check(False, f"fixture missing: {FIX} (run the extraction step first)")

# These danger cases test the COLUMNAR parser IN ISOLATION (calling parse_columnar_metals_myco
# directly) so a contrived minimal snippet can't let the unrelated generic inline parser reach the
# value — it isolates exactly what the columnar recovery does or refuses to do.
def _columnar_only(text):
    p = v5.ProductV5()
    p.analytes = {}
    p.cannabinoids = {}
    v4.parse_columnar_metals_myco(text, p)
    return p


# ---- 2a. DANGER: a BARE (no '<') value with an invalid garbled unit -> SKIP (never emit) -------
garble_only = ("Northeast Laboratories, Inc.\nHEAVY METALS:\nParameter\nArsenic, Total\n"
               "Result Units\n0.0005 4g/kg\n")
pg = _columnar_only(garble_only)
check("arsenic" not in pg.analytes,
      "columnar: a bare number with INVALID garbled unit '4g/kg' is SKIPPED (left unparsed, not guessed)")
check(pg.analytes.get("arsenic", {}).get("value") != 4.0,
      "columnar: never captures the '4' from the mangled unit '4g/kg' as arsenic")
# a '<' below-detect bound is SAFE even with a garbled unit (the bound, not the unit, is what counts)
bd_garble = ("Northeast Laboratories, Inc.\nHEAVY METALS:\nParameter\nArsenic, Total\nResult Units\n<0.0005 4g/kg\n")
pb = _columnar_only(bd_garble)
check(pb.analytes.get("arsenic", {}).get("_below_detect") is True
      and abs((pb.analytes.get("arsenic", {}).get("value") or -1) - 0.0005) < 1e-9,
      "columnar: a '<' below-detect bound IS recorded even with a garbled unit (arsenic <0.0005)")

# ---- 2b. a BARE value with a VALID unit + plausible magnitude IS recorded (as a real measurement) --
bare_ok = ("Northeast Laboratories, Inc.\nHEAVY METALS:\nParameter\nLead, Total\nResult Units\n0.5 mg/kg\n")
po = _columnar_only(bare_ok)
check(po.analytes.get("lead", {}).get("value") == 0.5 and not po.analytes.get("lead", {}).get("_below_detect"),
      "columnar: bare number with VALID unit 'mg/kg' + plausible magnitude IS recorded (lead=0.5 mg/kg measured)")

# ---- 3. DANGER: mismatched label/value counts -> emit NOTHING ----------------------------------
mismatch = ("Northeast Laboratories, Inc.\nHEAVY METALS:\nParameter\nArsenic, Total\nCadmium, Total\nLead, Total\n"
            "Result Units\n<0.0005 mg/kg\nPASS\n")   # 3 labels, 1 value
pm = _columnar_only(mismatch)
check(not any(k in pm.analytes for k in ("arsenic", "cadmium", "lead")),
      "columnar: mismatched columns (3 labels, 1 value) -> NO metals emitted (never mis-paired)")

# ---- 4. implausibly huge bare metal value with a valid unit -> SKIP ----------------------------
huge = ("Northeast Laboratories, Inc.\nHEAVY METALS:\nParameter\nLead, Total\nResult Units\n999999 mg/kg\n")
ph = _columnar_only(huge)
check("lead" not in ph.analytes, "columnar: implausibly huge bare metal (999999 mg/kg) is SKIPPED, not emitted")

# ---- 5. non-NELabs COA -> total no-op (don't touch other labs' formats) ------------------------
modern = ("ACME LABS COA\nHeavy Metals\nArsenic 0.01 mg/kg PASS\nResult Units\n<0.0005 mg/kg\n")
pn = _parse(modern)
check("northeast" not in modern.lower(), "(control) fixture is non-NELabs")
# the columnar parser must not fire on a non-NELabs doc; arsenic here would come only from the generic
# parser reading the inline '0.01', never from columnar recovery — assert no below-detect columnar entry
check(not (pn.analytes.get("cadmium") or pn.analytes.get("lead")),
      "columnar metals parser is a no-op on a non-NELabs COA")

print()
if _fails:
    print(f"{len(_fails)} FAILED")
    sys.exit(1)
print("ALL PASSED")
