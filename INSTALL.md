# CannaScope CT Beta Version 4 — Install & Run

Requires **Python 3.9+** and an internet connection. The launcher creates a local
virtual environment and installs dependencies on first run; later runs are fast.

The bundle (each OS zip) contains: `cannascope_ct_v4.py`, `ct_cannabis_names.py`,
`dba_overrides.csv`, `requirements.txt`, `README.md`, and the OS launcher.

---

## macOS

1. Download **`CannaScope-CT-V4-macos.zip`** and unzip it.
2. Read **READ-ME-FIRST-MAC.txt**.
3. **Right-click** `Run CannaScope CT.command` → **Open** → **Open**.
   (If blocked: System Settings → Privacy & Security → **Open Anyway**, or run
   `xattr -cr` on the folder in Terminal.)
4. The report appears as `CannaScope CT Beta Version 4 - Flagged Products - N.pdf`
   in the same folder.

Manual alternative (Terminal):
```bash
cd /path/to/unzipped/folder
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python cannascope_ct_v4.py
```

## Windows

1. Download **`CannaScope-CT-V4-windows.zip`** and unzip it (Extract All).
2. Double-click **`Run CannaScope CT.bat`**.
   (If SmartScreen warns: **More info → Run anyway**.)
3. The report appears as `CannaScope CT Beta Version 4 - Flagged Products - N.pdf`
   in the same folder.

Manual alternative (Command Prompt):
```bat
cd \path\to\unzipped\folder
py -m venv venv & venv\Scripts\activate.bat
pip install -r requirements.txt
python cannascope_ct_v4.py
```

## Linux

1. Download **`CannaScope-CT-V4-linux.zip`** and unzip it.
2. In a terminal:
   ```bash
   cd /path/to/unzipped/folder
   chmod +x run.sh
   ./run.sh
   ```
   (If `venv` creation fails: `sudo apt install python3-venv`. For OCR of scanned
   COAs: `sudo apt install tesseract-ocr`.)
3. The report appears as `CannaScope CT Beta Version 4 - Flagged Products - N.pdf`
   in the same folder.

---

## Common options

```bash
python cannascope_ct_v4.py --days 180     # widen the look-back window
python cannascope_ct_v4.py --threshold 5000   # stricter yeast/mold & aerobic CannaScope CT Standard
python cannascope_ct_v4.py --forms flower --days 30 --limit 50   # quick test
```
