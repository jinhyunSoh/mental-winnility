@echo off
rem  Builds Timer.exe from timer_overlay.py (keep both files in the same folder)
cd /d "%~dp0"

set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo [!] Python is not installed.
  echo     Install it from https://www.python.org/downloads/
  echo     and tick "Add python.exe to PATH" during setup, then run this file again.
  pause
  exit /b 1
)

echo [1/2] Installing PyInstaller...
%PY% -m pip install --upgrade pyinstaller || goto :fail

echo [2/2] Building Timer.exe...
%PY% -m PyInstaller --onefile --noconsole --clean --name Timer timer_overlay.py || goto :fail

if exist "dist\Timer.exe" (
  echo.
  echo Done!  dist\Timer.exe
  explorer dist
  pause
  exit /b 0
)

:fail
echo.
echo [!] Build failed. Check the messages above.
pause
exit /b 1
