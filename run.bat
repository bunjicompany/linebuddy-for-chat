@echo off
setlocal
cd /d "%~dp0"

if exist "dist\ItsumonoKaigyoForChat.exe" (
  "dist\ItsumonoKaigyoForChat.exe"
  exit /b %ERRORLEVEL%
)

if exist ".venv\Scripts\pythonw.exe" (
  ".venv\Scripts\pythonw.exe" "itsumono_kaigyo.py"
  exit /b %ERRORLEVEL%
)

pyw "itsumono_kaigyo.py" 2>nul
if %ERRORLEVEL% EQU 0 exit /b 0

pythonw "itsumono_kaigyo.py"
