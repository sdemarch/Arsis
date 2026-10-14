[CmdletBinding()]
param(
    [string]$DatabasePath
)

$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$backendSource = Join-Path $projectRoot "backend/src"
$originalLocation = (Get-Location).Path
$originalPythonPath = $env:PYTHONPATH

function Invoke-Seed {
    param(
        [Parameter(Mandatory)][string]$Command,
        [Parameter(Mandatory)][string[]]$PrefixArguments
    )

    $arguments = @($PrefixArguments) + @("-m", "arsis.dev.seed")
    if ($DatabasePath) {
        $resolvedDatabasePath = if ([System.IO.Path]::IsPathRooted($DatabasePath)) {
            [System.IO.Path]::GetFullPath($DatabasePath)
        }
        else {
            [System.IO.Path]::GetFullPath((Join-Path $projectRoot $DatabasePath))
        }
        $arguments += @("--database", $resolvedDatabasePath)
    }

    & $Command @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command ha restituito il codice $LASTEXITCODE."
    }
}

try {
    Set-Location -LiteralPath $projectRoot
    $env:PYTHONPATH = if ($originalPythonPath) {
        "$backendSource$([System.IO.Path]::PathSeparator)$originalPythonPath"
    }
    else {
        $backendSource
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        Invoke-Seed -Command "py" -PrefixArguments @("-3.14")
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        Invoke-Seed -Command "python" -PrefixArguments @()
    }
    else {
        throw "Python non disponibile: impossibile applicare il seed di sviluppo."
    }
}
finally {
    $env:PYTHONPATH = $originalPythonPath
    Set-Location -LiteralPath $originalLocation
}
