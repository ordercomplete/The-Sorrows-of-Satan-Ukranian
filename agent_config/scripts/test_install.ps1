# test_install.ps1 - Тест install.ps1 у тимчасовій папці + перевірка agent-lock.json
# Не містить жорстких шляхів: викликає install.ps1, що лежить поруч ($PSScriptRoot)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = $PSScriptRoot
$centralDir = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$tmp = Join-Path $env:TEMP ("csl_test_" + [guid]::NewGuid().ToString("N").Substring(0,8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
Write-Host "Test dir: $tmp"
Write-Host "Central repo: $centralDir"

$startDir = (Get-Location).Path
Set-Location $tmp
try {
    # git-репо, щоб sync-agent коректно показав git status, а .gitignore валідувався
    & git init -q
    & (Join-Path $scriptDir "install.ps1") "file:///$($centralDir -replace '\\','/')"
    Write-Host ""
    Write-Host "=== TEST RESULT ==="
    $lockOk = Test-Path ".\agent-lock.json"
    Write-Host ("agent-lock.json:             " + $lockOk)
    Write-Host ("AGENT canonical:             " + (Test-Path ".\AGENT\agents\Comfy-smart-lady.md"))
    Write-Host ("agent script:                " + (Test-Path ".\AGENT\scripts\anti_loop.py"))
    Write-Host ("clinerules hook:             " + (Test-Path ".\ .clinerules\hooks\Loops.json"))
    Write-Host ("clinerules stub:             " + (Test-Path ".\ .clinerules\agents\Comfy-smart-lady.md"))
    Write-Host ("opencode stub:               " + (Test-Path ".\ .opencode\agents\Comfy-smart-lady.md"))
    Write-Host ("agent_config present:        " + (Test-Path ".\agent_config\manifest.json"))

    if ($lockOk) {
        Write-Host ""
        Write-Host "--- sync-agent.py status (smoke test) ---"
        & python .\agent_config\scripts\sync-agent.py status --verbose

        # Кореневий .gitignore таргету НЕ повинен містити авто-блок Агента
        $rootGiTouched = $false
        if (Test-Path ".\ .gitignore") {
            $rootGiTouched = (Select-String -Path ".\ .gitignore" -Pattern "Comfy-smart-lady Agent").Count -gt 0
        }
        Write-Host ("root .gitignore NOT touched:  " + (-not $rootGiTouched))

        # Команда gitignore гарантує локальні .gitignore папок Агента
        Write-Host ""
        Write-Host "--- sync-agent.py gitignore ---"
        & python .\agent_config\scripts\sync-agent.py gitignore
        Write-Host ("local AGENT/.gitignore:        " + (Test-Path ".\AGENT\.gitignore"))
        Write-Host ("local .github/.gitignore:      " + (Test-Path ".\.github\.gitignore"))
        Write-Host ("local .clinerules/.gitignore:  " + (Test-Path ".\ .clinerules\.gitignore"))
    }
}
catch {
    Write-Host "TEST FAILED: $_" -ForegroundColor Red
}
finally {
    Set-Location $startDir
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    Write-Host "Cleanup done."
}