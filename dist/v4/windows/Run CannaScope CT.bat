@echo off
REM ===== CannaScope CT Beta Version 4 - Windows launcher =====
cd /d "%~dp0"
where py >/dev/null 2>/dev/null
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version >/dev/null 2>/dev/null
if errorlevel 1 (
  echo.
  echo Python was not found. Install Python 3.9+ from:
  echo    https://www.python.org/downloads/windows/
  echo and check "Add Python to PATH" during install.
  echo.
  pause
  exit /b 1
)
if not exist venv\ ( echo Setting up ^(first run only^)... & %PY% -m venv venv )
call venv\Scripts\activate.bat
echo Installing/updating dependencies...
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt
if errorlevel 1 ( echo Dependency install failed. See above. & pause & exit /b 1 )
echo.
echo Running CannaScope CT Beta Version 4 ^(last 60 days, all product types^)...
python cannascope_ct_v4.py %*
echo.
echo Done. Your numbered report ^(CannaScope CT Beta Version 4 - Flagged Products - N.pdf^)
echo is in this folder, with full details in "CannaScope CT - Flagged Product Results and Sources".
pause
