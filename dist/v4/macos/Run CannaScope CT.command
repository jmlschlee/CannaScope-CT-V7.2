#!/bin/bash
# ===== CannaScope CT Beta Version 4 - macOS launcher =====
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo; echo "Python 3 not found. Install from https://www.python.org/downloads/macos/"
  read -n 1 -s -r -p "Press any key to close..."; exit 1
fi
if [ ! -d venv ]; then echo "Setting up (first run only)..."; python3 -m venv venv; fi
source venv/bin/activate
echo "Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt || { echo "Dependency install failed."; read -n 1 -s -r -p "Press any key..."; exit 1; }
echo; echo "Running CannaScope CT Beta Version 4 (last 60 days, all product types)..."; echo
python cannascope_ct_v4.py "$@"
echo; echo 'Done. Your numbered report (CannaScope CT Beta Version 4 - Flagged Products - N.pdf)'
echo 'is in this folder; full details are in "CannaScope CT - Flagged Product Results and Sources".'
read -n 1 -s -r -p "Press any key to close..."
