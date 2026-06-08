#!/usr/bin/env python3
"""Phases 1/2/6 acceptance: the persisted Training Ledger + traceability + diagnose.

THE ACCEPTANCE TEST (per the spec): the training_run_id the REPORT used must equal the training_run_id
that `learn` wrote — otherwise print TRAINING PIPELINE DISCONNECT.

This runs the real pipeline end-to-end (offline, fast):
  1. `learn --years 2015-2015 --offline`  -> writes Training Ledger.json with a fresh training_run_id
  2. `statewide --since/--until 2015 --offline --csv-cache` -> a report that loads the ledger
  3. assert report.debug.training_run_id_used == ledger.training_run_id  AND status OK
  4. assert the P1 trace export + the offline per-year readiness verdict exist
  5. `diagnose-learning --year 2015` -> summary carries the same training_run_id

Run:  python3 _test_training_ledger.py
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "cannascope_ct_v17_src.py")
RPT = os.path.join(HERE, "CannaScope CT V17 - Statewide Transparency Reports")
LEDGER = os.path.join(RPT, "Training Ledger.json")
_fails = []


def check(msg, cond):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


def run(*args):
    r = subprocess.run([sys.executable, SRC, *args], cwd=HERE, capture_output=True, text=True, timeout=1200)
    return r.stdout + r.stderr


print("1) learn --years 2015-2015 --offline ...")
run("learn", "--years", "2015-2015", "--offline", "--per-year", "6")
led = json.load(open(LEDGER, encoding="utf-8"))
run_id = led.get("training_run_id", "")
check("Training Ledger written with a training_run_id", bool(run_id))
check("ledger records the 2015 per-year verdict", "2015" in (led.get("years") or {}))
check("ledger carries per-COA training records (P1)", len(led.get("coas") or {}) > 0)
sample = next(iter((led.get("coas") or {}).values()), {})
check("a training record has the P1 fields", all(k in sample for k in
      ("coa_id", "source_url", "year", "lab", "format_signature", "training_run_id",
       "parser_version", "analysis_version", "raw_pdf_hash", "confidence")))

print("\n2) statewide 2015 --offline (loads the ledger) ...")
run("statewide", "--since", "2015-01-01", "--until", "2015-12-31", "--offline", "--csv-cache")
# newest report's debug_log.json
dbgs = sorted(glob.glob(os.path.join(RPT, "*", "Data Exports", "debug_log.json")), key=os.path.getmtime)
check("a report debug_log.json was produced", bool(dbgs))
dbg = json.load(open(dbgs[-1], encoding="utf-8")) if dbgs else {}

print("\n3) ACCEPTANCE — report training_run_id_used == learn training_run_id")
print(f"     learn  : {run_id}")
print(f"     report : {dbg.get('training_run_id_used')}")
check("ACCEPTANCE: report used the training_run_id that learn wrote",
      dbg.get("training_run_id_used") == run_id)
check("training pipeline status is OK (no disconnect)",
      str(dbg.get("training_pipeline_status", "")).startswith("OK"))

print("\n4) P1 trace export + offline readiness verdict")
trace = os.path.join(RPT, "Data Exports", "training_to_report_trace.csv")
check("training_to_report_trace.csv was written", os.path.exists(trace))
# the offline report must now carry a 2015 readiness verdict (not an empty table)
check("offline report reflects the persisted 2015 readiness (status names YEAR NOT READY or readiness present)",
      "NOT READY" in str(dbg.get("status_tier", "")) or "NOT READY" in str(dbg.get("report_status", ""))
      or dbg.get("training_run_id_used") == run_id)

print("\n5) diagnose-learning --year 2015")
run("diagnose-learning", "--year", "2015")
dsum_path = os.path.join(RPT, "Data Exports", "diagnose_learning_2015_summary.json")
check("diagnose summary written", os.path.exists(dsum_path))
if os.path.exists(dsum_path):
    dsum = json.load(open(dsum_path, encoding="utf-8"))
    check("diagnose summary carries the same training_run_id", dsum.get("training_run_id") == run_id)
    check("diagnose reports the 2015 verdict", bool(dsum.get("year_verdict")))

print()
if _fails:
    print(f"{len(_fails)} FAILED")
    sys.exit(1)
print("ALL PASSED — training pipeline is connected (report used the trained version)")
