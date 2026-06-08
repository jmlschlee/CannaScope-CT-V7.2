#!/usr/bin/env python3
"""Acceptance test for the cross-platform 're-run OCR up to 5x' rule.

Verifies the isolated OCR path (`_isolated_ocr_pdf`) escalates the approach across UP TO 5 attempts and
gives up ONLY after all 5 come back empty — never fabricating a value — and that it STOPS as soon as an
attempt yields text. Also checks the in-process fallback `cannascope_ct_v4.ocr_pdf` uses a 5-scale ladder.

Run:  python3 _test_ocr_escalation.py
"""
import sys
import cannascope_ct_v17_src as cc
import cannascope_ct_v4 as v4

_fails = []
def check(cond, msg):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


# ---- isolate _isolated_ocr_pdf from the real engine/cache/backoff ----
cc._ocr_cache_key = lambda src: ""              # skip cache get/put
cc._ocr_cache_get = lambda k: None
cc._ocr_cache_put = lambda k, t: None
cc._ocr_backend_available = lambda: True
cc._adaptive_backoff = lambda: None
cc._memory_critical = lambda: False
import os as _os
cc._OCR_WORKER = __file__                        # any existing file so os.path.exists() passes

calls = []
def _stub_all_empty(src, max_pages, timeout, scale=2.0):
    calls.append((scale, timeout))
    return 0, b""                                # rc=0, empty output -> escalate
cc._run_ocr_worker = _stub_all_empty

# 1) all attempts empty -> exactly 5 escalating attempts, then "" (never a fabricated value)
calls.clear()
out = cc._isolated_ocr_pdf("fake.pdf")
check(out == "", "all-empty OCR returns '' (no value fabricated)")
check(len(calls) == 5, f"OCR retried UP TO 5 attempts (got {len(calls)})")
scales = [c[0] for c in calls]
check(scales == sorted(scales), f"each attempt escalates DPI (non-decreasing scales: {scales})")
check(scales[-1] >= 4.0 and scales[0] <= 2.0, f"ladder spans normal->max DPI ({scales[0]}..{scales[-1]})")
check(len(set(scales)) >= 3, f"the approach actually changes across attempts (distinct scales: {sorted(set(scales))})")

# 2) text appears on attempt 4 -> STOP at 4 (don't waste the 5th)
state = {"n": 0}
def _stub_succeed_on_4(src, max_pages, timeout, scale=2.0):
    calls.append((scale, timeout)); state["n"] += 1
    return (0, b"Total Yeast & Mold 1200 CFU/g PASS") if state["n"] == 4 else (0, b"")
cc._run_ocr_worker = _stub_succeed_on_4
calls.clear()
out = cc._isolated_ocr_pdf("fake.pdf")
check("Yeast" in out, "returns the recovered text once an attempt yields data")
check(len(calls) == 4, f"stops as soon as text is found (4 attempts, not 5; got {len(calls)})")

# 3) in-process fallback ocr_pdf uses a 5-scale ladder (cross-platform: tesseract path too)
import inspect
srcimpl = inspect.getsource(v4.ocr_pdf)
check(srcimpl.count("2.6") >= 1 and srcimpl.count("3.2") >= 1 and srcimpl.count("4.0") >= 1,
      "v4.ocr_pdf body has the escalating 5-scale ladder (2.0/2.6/3.2/4.0)")

print()
if _fails:
    print(f"{len(_fails)} FAILED"); sys.exit(1)
print("ALL PASSED")
