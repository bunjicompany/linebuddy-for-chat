param(
    [ValidateSet("major", "minor", "patch", "none")]
    [string]$VersionBump = "patch"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
$env:VERSION_BUMP = $VersionBump
& ".\.venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm ItsumonoKaigyo.spec

Write-Host "Built: $Root\dist\ItsumonoKaigyoForChat.exe"
