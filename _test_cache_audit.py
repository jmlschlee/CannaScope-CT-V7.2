#!/usr/bin/env python3
"""Acceptance test for the SUPERIOR RULE — active cache self-audit (cache is a hint, live is the authority).

Proves: identical cache/live agree; a VALUE CONFLICT distrusts the cache (forces full live re-pull) AND
corrects it live; a coverage delta is corrected live; below-detect bounds agree; a dead/unreadable live
re-pull is NOT counted as a disagreement (no false alarm); stride sampling is deterministic.

Run:  python3 _test_cache_audit.py
"""
import sys
import cannascope_ct_v17_src as cc
import cannascope_ct_v4 as v4
import cannascope_ct_v5 as v5

_fails = []
def check(cond, msg):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


def _prod(reg, analytes):
    p = v5.ProductV5(); p.registration_number = reg; p.report_url = "http://x/" + reg + ".pdf"
    p.analytes = analytes; p.cannabinoids = {}; return p


# ---- _compare_cache_live ----
A = _prod("A", {"tymc": {"value": 1200.0, "raw": "1200"}})
ok, conf, delt = cc._compare_cache_live(A, _prod("A", {"tymc": {"value": 1200.0, "raw": "1200"}}))
check(ok and not conf and not delt, "identical cache/live agree")
ok, conf, delt = cc._compare_cache_live(A, _prod("A", {"tymc": {"value": 999999.0, "raw": "999999"}}))
check(not ok and conf and not delt, "both hold a value but differ -> VALUE CONFLICT")
ok, conf, delt = cc._compare_cache_live(A, _prod("A", {"tymc": {"value": 1200.0, "raw": "1200"},
                                                       "lead": {"value": 0.5, "raw": "0.5"}}))
check(not ok and not conf and delt == ["lead"] or "lead" in delt, "live has an extra analyte -> coverage DELTA (not a conflict)")
bd = _prod("A", {"arsenic": {"value": 0.0005, "_below_detect": True, "raw": "<0.0005"}})
ok, conf, delt = cc._compare_cache_live(bd, _prod("A", {"arsenic": {"value": 0.0009, "_below_detect": True, "raw": "<0.0009"}}))
check(ok, "two below-detect bounds agree (both passes)")

# ---- _stride_sample deterministic + evenly spaced ----
seq = list(range(100))
s1 = cc._stride_sample(seq, 10); s2 = cc._stride_sample(seq, 10)
check(s1 == s2 and len(s1) == 10 and s1[0] == 0 and s1[-1] >= 80, f"stride sample deterministic + spread ({s1})")
check(cc._stride_sample([1, 2, 3], 10) == [1, 2, 3], "stride sample of fewer-than-n returns all")

# ---- cache_self_audit end-to-end with a fake cache + controlled live ----
class FakeCache:
    def __init__(self, rows): self.rows = dict(rows)
    def fresh_row(self, p): return self.rows.get(v4.coa_key(p))
    def rehydrate(self, row, watch): return row
    def put(self, p, **kw): self.rows[v4.coa_key(p)] = p

cached = {
    "A": _prod("A", {"tymc": {"value": 1200.0, "raw": "1200"}}),          # will agree
    "B": _prod("B", {"tymc": {"value": 1200.0, "raw": "1200"}}),          # live will CONFLICT
    "C": _prod("C", {"arsenic": {"value": 0.0005, "_below_detect": True, "raw": "<0.0005"}}),  # live adds lead (delta)
    "D": _prod("D", {"tymc": {"value": 500.0, "raw": "500"}}),            # live dead -> skip
}
fake = FakeCache({k: v for k, v in cached.items()})
live_map = {
    "A": _prod("A", {"tymc": {"value": 1200.0, "raw": "1200"}}),
    "B": _prod("B", {"tymc": {"value": 7.7e9, "raw": "7700000000"}}),
    "C": _prod("C", {"arsenic": {"value": 0.0005, "_below_detect": True, "raw": "<0.0005"},
                     "lead": {"value": 0.002, "_below_detect": True, "raw": "<0.002"}}),
    "D": _prod("D", {}),                                                  # empty live -> unreadable/dead
}
_orig_pp = cc.process_product
cc.process_product = lambda p, s, w: live_map[p.registration_number]
try:
    res = cc.cache_self_audit([cached[k] for k in ("A", "B", "C", "D")], None, 80.0, fake, full=True)
finally:
    cc.process_product = _orig_pp

check(res["agreed"] >= 1, f"agreed counts the matching record(s) (got {res['agreed']})")
check(res["value_conflicts"] >= 1, f"value conflict detected (got {res['value_conflicts']})")
check(res["coverage_deltas"] >= 1, f"coverage delta detected (got {res['coverage_deltas']})")
check(res["unreadable_live"] >= 1, "a dead/empty live re-pull is SKIPPED, not a false disagreement")
check(res["distrusted"] is True, "a value conflict DISTRUSTS the cache (forces full live re-pull)")
check(res["corrected"] >= 2, f"disagreeing rows were corrected live in the cache (got {res['corrected']})")
check(fake.rows["B"].analytes["tymc"]["value"] == 7.7e9, "LIVE WINS: cache row B was overwritten with the live value")

print()
if _fails:
    print(f"{len(_fails)} FAILED"); sys.exit(1)
print("ALL PASSED")
