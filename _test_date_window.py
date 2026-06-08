#!/usr/bin/env python3
"""Date-window integrity regression (spec item 7). For each requested window, load the real COA cache,
apply the SAME enforcement the report uses (cannascope_ct_v17_src.enforce_date_window / validate_date_window
on the COA test date), and assert:
  - earliest in-window test date >= requested start
  - latest   in-window test date <= requested end
  - ZERO out-of-window records survive
  - hard validation returns PASS
  - (PDF window == CSV window == dataset window: all three are rendered from the same date_trace, so a
    PASS here guarantees they agree.)
Run: python3 _test_date_window.py
"""
import csv, sys
import cannascope_ct_v17_src as cc
import cannascope_ct_v5 as v5

CACHE = "CannaScope CT V17 - Statewide Transparency Reports/COA Data Cache.csv"

RANGES = [
    ("2015-only", (2015, 1, 1), (2015, 12, 31)),
    ("2016-only", (2016, 1, 1), (2016, 12, 31)),
    ("2017-only", (2017, 1, 1), (2017, 12, 31)),
    ("2018-only", (2018, 1, 1), (2018, 12, 31)),
    ("2019-only", (2019, 1, 1), (2019, 12, 31)),
    ("2020-only", (2020, 1, 1), (2020, 12, 31)),
    ("2015-2020", (2015, 1, 1), (2020, 12, 31)),
    ("2021-2023", (2021, 1, 1), (2023, 12, 31)),
    ("2024-2026", (2024, 1, 1), (2026, 12, 31)),
]


def _load():
    import json
    recs = []
    for r in csv.DictReader(open(CACHE, encoding="utf-8")):
        p = v5.ProductV5()
        td = ""
        try:
            td = (json.loads(r.get("_extra") or "{}") or {}).get("testing_date", "")
        except Exception:
            td = ""
        p.testing_date = td or ""
        p.approval_date = r.get("approval_date", "") or ""
        recs.append(p)
    return recs


def main():
    recs = _load()
    print(f"loaded {len(recs):,} cached records\n")
    fails = 0
    for label, lo, hi in RANGES:
        inw, out, nod, trace = cc.enforce_date_window(recs, lo, hi)
        ok, msg = cc.validate_date_window(inw, lo, hi)
        # The integrity guarantee: ZERO records with a CONFIRMABLE (parseable) COA test date may fall
        # OUTSIDE the window. Records whose COA test date did NOT parse are intentionally placed in-window
        # by their registry APPROVAL date (a DISCLOSED coverage decision, surfaced in the report's
        # Date-Window Integrity section) and are NOT leaks — but their count must EXACTLY match the trace's
        # disclosed included_by_approval_date_fallback (so the fallback can never silently grow).
        true_leaks = [p for p in inw if (cc._record_test_date_tuple(p) is not None)
                      and not (lo <= cc._record_test_date_tuple(p) <= hi)]
        approval_admitted = [p for p in inw if cc._record_test_date_tuple(p) is None]
        disclosed = trace.get("included_by_approval_date_fallback", 0)
        earliest = trace["actual_earliest_test_date"]
        latest = trace["actual_latest_test_date"]
        passed = (ok and not true_leaks and len(approval_admitted) == disclosed
                  and (not earliest or earliest >= cc._fmt_tuple(lo))
                  and (not latest or latest <= cc._fmt_tuple(hi)))
        fails += 0 if passed else 1
        print(f"  [{'PASS' if passed else 'FAIL'}] {label:10} window={cc._fmt_tuple(lo)}..{cc._fmt_tuple(hi)} "
              f"in={trace['records_after_filter']:,} out={trace['excluded_out_of_window']:,} "
              f"no_date={trace['excluded_no_test_date']:,} appr_fallback={disclosed:,} "
              f"validation={'PASS' if ok else 'FAIL:'+msg} true_leaks={len(true_leaks)}")
    print()
    if fails:
        print(f"DATE-WINDOW REGRESSION: {fails} range(s) FAILED"); sys.exit(1)
    print("DATE-WINDOW REGRESSION: ALL RANGES PASSED")


if __name__ == "__main__":
    main()
