#!/usr/bin/env python3
"""Acceptance test for the plausibility cross-check (units/ranges) that drives 'when in doubt, go live'
and the publication plausibility gate. A WRONG safety value must never pass; below-detect bounds always pass.

Run:  python3 _test_plausibility.py
"""
import sys
import cannascope_ct_v17_src as cc
import cannascope_ct_v5 as v5

_fails = []
def check(cond, msg):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


def _p(analytes=None, cannabinoids=None):
    p = v5.ProductV5(); p.analytes = analytes or {}; p.cannabinoids = cannabinoids or {}
    return p


# --- plausible cases (must pass) ---
ok, _ = cc._measurements_plausible(_p(analytes={
    "arsenic": {"value": 0.0005, "_below_detect": True, "raw": "<0.0005"},
    "tymc": {"value": 1200.0, "raw": "1200"}}, cannabinoids={"total_thc": {"value": 24.1}}))
check(ok, "normal below-detect metal + 1200 CFU/g microbial + 24% THC is plausible")

ok, _ = cc._measurements_plausible(_p(analytes={"lead": {"value": 0.5, "raw": "0.5"}}))
check(ok, "a real small metal measurement (0.5 mg/kg) is plausible")

# below-detect bound with a garbled-but-irrelevant magnitude is still a pass (it's < detection)
ok, _ = cc._measurements_plausible(_p(analytes={"afla_b1": {"value": 5.0, "_below_detect": True, "raw": "<5"}}))
check(ok, "below-detect mycotoxin bound is plausible (a pass)")

# --- implausible cases (must FAIL the check = would be re-pulled / gated) ---
bad, why = cc._measurements_plausible(_p(analytes={"tymc": {"value": 4e14, "raw": "4e14"}}))
check(not bad, "microbial 4e14 CFU/g is implausible (OCR/scientific artifact)")

bad, _ = cc._measurements_plausible(_p(analytes={"lead": {"value": 5000.0, "raw": "5000"}}))
check(not bad, "heavy-metal 5000 mg/kg is implausible (garbled)")

bad, _ = cc._measurements_plausible(_p(cannabinoids={"total_thc": {"value": 150.0}}))
check(not bad, "cannabinoid 150% is impossible (>100%)")

bad, _ = cc._measurements_plausible(_p(analytes={"arsenic": {"value": -1.0, "raw": "-1"}}))
check(not bad, "negative analyte value is implausible")

# a below-detect microbial with a huge bound is NOT a false positive (it's under detection)
ok, _ = cc._measurements_plausible(_p(analytes={"tymc": {"value": 1e14, "_below_detect": True, "raw": "<1e14"}}))
check(ok, "below-detect microbial bound does not trip the plausibility gate")

print()
if _fails:
    print(f"{len(_fails)} FAILED"); sys.exit(1)
print("ALL PASSED")
