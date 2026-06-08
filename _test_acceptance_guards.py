#!/usr/bin/env python3
"""Acceptance tests for the two 'MASSIVE FAILURE' guards:
  NN5 — an empty report (COAs in window but no information) must fail loud (`_report_is_blank` True).
  NN6 — out-of-range data must fail validation (`validate_date_window` returns not-ok).

Run:  python3 _test_acceptance_guards.py
"""
import sys
import cannascope_ct_v17_src as cc
import cannascope_ct_v5 as v5

_fails = []
def check(cond, msg):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


def _rec(testing_date="", analytes=None):
    p = v5.ProductV5(); p.analytes = analytes or {}; p.cannabinoids = {}
    p.testing_date = testing_date; p.approval_date = ""
    return p


# ---- NN5: blank-report detection ----
empty1 = _rec(); empty2 = _rec()
withdata = _rec(analytes={"tymc": {"value": 1200.0, "raw": "1200"}})
check(cc._report_is_blank([], []) is False, "no in-window records -> not 'blank' (handled by the separate exit)")
check(cc._report_is_blank([empty1, empty2], []) is True,
      "COAs in window but NOTHING parsed and NOTHING published -> blank report (FAIL LOUD)")
check(cc._report_is_blank([empty1, withdata], []) is False,
      "at least one record has data -> NOT blank (report has information)")
check(cc._report_is_blank([empty1, empty2], [withdata]) is False,
      "something published -> NOT blank")

# ---- NN6: out-of-range detection (date-window hard validation) ----
inw = _rec(testing_date="2015-06-01")
out = _rec(testing_date="2019-06-01")
ok, msg = cc.validate_date_window([inw], (2015, 1, 1), (2015, 12, 31))
check(ok, "an in-window record passes date validation")
ok, msg = cc.validate_date_window([inw, out], (2015, 1, 1), (2015, 12, 31))
check(not ok, f"an out-of-window record FAILS date validation (msg: {msg})")
# a record with no confirmable date at all must also not silently pass as in-window
nodate = _rec(testing_date="")
ok, _ = cc.validate_date_window([nodate], (2015, 1, 1), (2015, 12, 31))
check(not ok, "a record with no confirmable date does not pass as in-window")

print()
if _fails:
    print(f"{len(_fails)} FAILED"); sys.exit(1)
print("ALL PASSED")
