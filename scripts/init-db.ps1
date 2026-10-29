[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [string]$DatabasePath = "data/arsis.db",
    [switch]$SkipDriverInstall,
    [switch]$SkipCodeGeneration
)

$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$databaseProject = Join-Path $projectRoot "database"
$changelogFile = "changelog/db.changelog-master.yaml"
$lpmHome = Join-Path $databaseProject ".lpm"
$liquibaseLibs = Join-Path $databaseProject "liquibase_libs"
$originalLocation = (Get-Location).Path
$originalLiquibaseHome = $env:LIQUIBASE_HOME

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory)][string]$Command,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command ha restituito il codice $LASTEXITCODE."
    }
}

function Assert-SupportedJava {
    $javaCommand = if ($env:JAVA_HOME) {
        Join-Path $env:JAVA_HOME "bin/java.exe"
    }
    else {
        (Get-Command java -ErrorAction SilentlyContinue).Source
    }

    if (-not $javaCommand -or -not (Test-Path -LiteralPath $javaCommand -PathType Leaf)) {
        throw "Java non è disponibile. Liquibase 5 richiede Java 17 o superiore."
    }

    $versionOutput = (& $javaCommand -version 2>&1 | Select-Object -First 1).ToString()
    $versionMatch = [regex]::Match($versionOutput, 'version "(?<version>[0-9]+)(?:\.(?<minor>[0-9]+))?')
    if (-not $versionMatch.Success) {
        throw "Impossibile determinare la versione Java da: $versionOutput"
    }

    $majorVersion = [int]$versionMatch.Groups["version"].Value
    if ($majorVersion -eq 1 -and $versionMatch.Groups["minor"].Success) {
        $majorVersion = [int]$versionMatch.Groups["minor"].Value
    }
    if ($majorVersion -lt 17) {
        throw "Java $majorVersion rilevato tramite JAVA_HOME. Liquibase 5 richiede Java 17 o superiore; aggiornare JAVA_HOME."
    }
}

function Install-SqliteDriver {
    $lpmExecutable = Join-Path $lpmHome "lpm.exe"
    $packageManifest = Join-Path $databaseProject "lib/packages.json"

    if (-not (Test-Path -LiteralPath $lpmExecutable -PathType Leaf)) {
        Write-Host "Scarico Liquibase Package Manager nella cartella del progetto..."
        Invoke-CheckedCommand -Command "liquibase" -Arguments @(
            "lpm",
            "--lpmHome=$lpmHome",
            "--download=true"
        )
    }

    $env:LIQUIBASE_HOME = $databaseProject
    New-Item -ItemType Directory -Force -Path (Join-Path $databaseProject "lib") | Out-Null

    if (-not (Test-Path -LiteralPath $packageManifest -PathType Leaf)) {
        Write-Host "Aggiorno il catalogo dei package Liquibase..."
        Invoke-CheckedCommand -Command $lpmExecutable -Arguments @("update")
    }

    Write-Host "Installo il driver JDBC SQLite dichiarato in liquibase.json..."
    Invoke-CheckedCommand -Command $lpmExecutable -Arguments @("install")
}

try {
    Set-Location -LiteralPath $databaseProject

    if (-not (Get-Command liquibase -ErrorAction SilentlyContinue)) {
        throw "Liquibase non è disponibile. Installare Liquibase 5 e aggiungerlo al PATH."
    }
    Assert-SupportedJava

    $resolvedDatabasePath = if ([System.IO.Path]::IsPathRooted($DatabasePath)) {
        [System.IO.Path]::GetFullPath($DatabasePath)
    }
    else {
        [System.IO.Path]::GetFullPath((Join-Path $projectRoot $DatabasePath))
    }

    $dataDirectory = Split-Path -Parent $resolvedDatabasePath
    New-Item -ItemType Directory -Force -Path $dataDirectory | Out-Null

    $driver = Get-ChildItem -LiteralPath $liquibaseLibs -Filter "sqlite-jdbc-*.jar" -File -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        Select-Object -First 1

    if (-not $driver) {
        if ($SkipDriverInstall) {
            throw "Driver JDBC SQLite assente in $liquibaseLibs."
        }
        Install-SqliteDriver
        $driver = Get-ChildItem -LiteralPath $liquibaseLibs -Filter "sqlite-jdbc-*.jar" -File |
            Sort-Object Name -Descending |
            Select-Object -First 1
    }

    $jdbcPath = $resolvedDatabasePath.Replace("\", "/")
    $liquibaseCommand = if ($ValidateOnly) { "validate" } else { "update" }

    Write-Host "Database: $resolvedDatabasePath"
    Write-Host "Eseguo Liquibase $liquibaseCommand..."
    Invoke-CheckedCommand -Command "liquibase" -Arguments @(
        "--changelog-file=$changelogFile",
        "--url=jdbc:sqlite:$jdbcPath",
        "--driver=org.sqlite.JDBC",
        $liquibaseCommand
    )

    if ($ValidateOnly) {
        Write-Host "Changelog Liquibase valido." -ForegroundColor Green
    }
    else {
        if (-not $SkipCodeGeneration) {
            $generator = Join-Path $projectRoot "scripts/generate_backend_schema.py"
            Write-Host "Rigenero modelli SQLAlchemy e DTO Pydantic..."

            if (Get-Command py -ErrorAction SilentlyContinue) {
                Invoke-CheckedCommand -Command "py" -Arguments @(
                    "-3.14",
                    $generator,
                    "--database",
                    $resolvedDatabasePath
                )
            }
            elseif (Get-Command python -ErrorAction SilentlyContinue) {
                Invoke-CheckedCommand -Command "python" -Arguments @(
                    $generator,
                    "--database",
                    $resolvedDatabasePath
                )
            }
            else {
                throw "Python non disponibile: impossibile rigenerare il codice backend."
            }
        }

        Write-Host "Database Arsis inizializzato e allineato." -ForegroundColor Green
    }
}
finally {
    $env:LIQUIBASE_HOME = $originalLiquibaseHome
    Set-Location -LiteralPath $originalLocation
}
