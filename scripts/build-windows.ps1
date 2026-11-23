[CmdletBinding()]
param(
    # Riusa la build Angular esistente in frontend\dist.
    [switch]$SkipFrontend,
    # Ferma il processo dopo l'exe, senza creare l'installer.
    [switch]$SkipInstaller,
    # Versione mostrata e usata nel nome dell'installer. Per le release GitHub
    # riceve il tag; senza valore usa la versione dichiarata dal backend.
    [string]$Version
)

# Crea build\pyinstaller\dist\Arsis\Arsis.exe e, se Inno Setup 6 e installato,
# build\installer\Arsis-Setup-<versione>.exe. Prerequisiti: Python 3.14, Node.js 24.

$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$buildDir = Join-Path $projectRoot "build"
$venv = Join-Path $buildDir "venv"
$python = Join-Path $venv "Scripts\python.exe"

function Invoke-Checked {
    param([Parameter(Mandatory)][string]$Command, [string[]]$Arguments = @())
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command ha restituito il codice $LASTEXITCODE." }
}

if ([string]::IsNullOrWhiteSpace($Version)) {
    $versionLine = Select-String -Path (Join-Path $projectRoot "backend\pyproject.toml") -Pattern '^version = "(.+)"' | Select-Object -First 1
    $version = $versionLine.Matches[0].Groups[1].Value
}
else {
    $version = $Version.Trim()
}
Write-Host "Arsis $version" -ForegroundColor Cyan
New-Item -ItemType Directory -Force $buildDir | Out-Null

if (-not $SkipFrontend) {
    Write-Host "Compilazione frontend..."
    Push-Location (Join-Path $projectRoot "frontend")
    try {
        Invoke-Checked "npm" @("ci")
        Invoke-Checked "npm" @("run", "build")
    }
    finally { Pop-Location }
}
if (-not (Test-Path (Join-Path $projectRoot "frontend\dist\arsis\browser\index.html"))) {
    throw "Build Angular non trovata in frontend\dist\arsis\browser."
}

if (-not (Test-Path $python)) {
    Write-Host "Creazione ambiente di build in $venv..."
    Invoke-Checked "py" @("-3.14", "-m", "venv", $venv)
}
Write-Host "Installazione backend e PyInstaller..."
Invoke-Checked $python @("-m", "pip", "install", "--quiet", "--upgrade", "pip")
Invoke-Checked $python @("-m", "pip", "install", "--quiet", (Join-Path $projectRoot "backend"), "pyinstaller>=6.16,<7", "pillow>=11,<12")

Write-Host "Icona da frontend\public\favicon.png..."
$favicon = Join-Path $projectRoot "frontend\public\favicon.png"
$icon = Join-Path $buildDir "arsis.ico"
Invoke-Checked $python @("-c", "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2], sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])", $favicon, $icon)

Write-Host "PyInstaller..."
Invoke-Checked $python @(
    "-m", "PyInstaller", (Join-Path $projectRoot "packaging\arsis.spec"),
    "--noconfirm",
    "--distpath", (Join-Path $buildDir "pyinstaller\dist"),
    "--workpath", (Join-Path $buildDir "pyinstaller\work")
)
$exe = Join-Path $buildDir "pyinstaller\dist\Arsis\Arsis.exe"
if (-not (Test-Path $exe)) { throw "Arsis.exe non generato." }
Write-Host "Eseguibile: $exe" -ForegroundColor Green

if ($SkipInstaller) { return }
$iscc = @(
    (Get-Command "ISCC.exe" -ErrorAction SilentlyContinue).Source,
    (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $iscc) {
    Write-Warning "Inno Setup 6 non trovato: installer non creato. Installarlo (winget install JRSoftware.InnoSetup) e rilanciare."
    return
}
Write-Host "Inno Setup..."
Invoke-Checked $iscc @("/Q", "/DAppVersion=$version", (Join-Path $projectRoot "packaging\arsis.iss"))
Write-Host "Installer: $(Join-Path $buildDir "installer\Arsis-Setup-$version.exe")" -ForegroundColor Green
