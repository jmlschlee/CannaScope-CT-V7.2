#!/usr/bin/env bash
# ===== CannaScope CT Beta Version 4 - Linux launcher =====
cd "$(dirname "$0")" || exit 1
command -v python3 >/dev/null 2>&1 || { echo "Install python3 (e.g. sudo apt install python3 python3-venv)"; exit 1; }
[ -d venv ] || { echo "Setting up (first run only)..."; python3 -m venv venv || { echo "Try: sudo apt install python3-venv"; exit 1; }; }
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt || { echo "Dependency install failed."; exit 1; }
echo; echo "Running CannaScope CT Beta Version 4 (last 60 days, all product types)..."; echo
python cannascope_ct_v4.py "$@"
echo; echo 'Done. Your numbered report (CannaScope CT Beta Version 4 - Flagged Products - N.pdf)'
echo 'is in this folder; full details are in "CannaScope CT - Flagged Product Results and Sources".'
