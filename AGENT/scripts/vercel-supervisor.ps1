#Requires -Version 5.1
<#
.SYNOPSIS
    Vercel AI Gateway Supervisor - автоматичний перезапуск чату при помилках Vercel.
.DESCRIPTION
    Моніторить процес OpenCode і автоматично перезапускає його при помилках типу
    "Failed to create stream: inference request failed..." з експоненціальним backoff.
.PARAMETER MaxRestarts
    Максимальна кількість перезапусків (за замовчуванням: 5)
.EXAMPLE
    .\vercel-supervisor.ps1
    Запуск з параметрами за замовчуванням
#>

[CmdletBinding()]
param(
    [int]$MaxRestarts = 5,
    [int]$InitialDelayMs = 3000,
    [int]$MaxDelayMs = 60000,
    [double]$ExponentialBase = 2.0,
    [string]$Command = "opencode",
    [string[]]$Arguments = @("run"),
    [string]$WorkingDirectory = "D:\GEN\Comfy-smart-lady-agent"
)

$Config = @{
    MaxRestarts       = $MaxRestarts
    InitialDelayMs    = $InitialDelayMs
    MaxDelayMs        = $MaxDelayMs
    ExponentialBase   = $ExponentialBase
    Command           = $Command
    Arguments         = $Arguments
    WorkingDirectory  = $WorkingDirectory
    LogDir            = Join-Path $WorkingDirectory "AGENT\memories_agent\logs\vercel-supervisor"
    ErrorPatterns     = @(
        "Failed to create stream"
        "inference request failed"
        "failed to invoke model"
        "failed to send request"
        "giving up after.*attempt"
        "ai-gateway\.vercel\.sh"
        "failed to generate stream from Vercel"
    )
}

if (-not (Test-Path $Config.LogDir)) {
    New-Item -ItemType Directory -Path $Config.LogDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd"
$Config.LogFile = Join-Path $Config.LogDir "supervisor_$timestamp.log"
$Config.StdErrFile = Join-Path $Config.LogDir "agent_stderr_$timestamp.log"

function Write-Log {
    param([Parameter(Mandatory)][string]$Message, [ValidateSet("INFO","WARN","ERROR","SUCCESS")][string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$ts] [$Level] $Message"
    switch ($Level) {
        "ERROR"   { Write-Host $logEntry -ForegroundColor Red }
        "WARN"    { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default   { Write-Host $logEntry }
    }
    [System.IO.File]::AppendAllText($Config.LogFile, $logEntry + "`n", [System.Text.Encoding]::UTF8)
}

function Get-BackoffDelay {
    param([int]$Attempt)
    $delay = $Config.InitialDelayMs * [Math]::Pow($Config.ExponentialBase, $Attempt - 1)
    return [Math]::Min($delay, $Config.MaxDelayMs)
}

function Test-VercelError {
    param([string]$LogFilePath)
    if (-not (Test-Path $LogFilePath)) { return $null }
    $content = Get-Content $LogFilePath -Tail 100 -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $content) { return $null }
    $contentText = $content -join "`n"
    foreach ($pattern in $Config.ErrorPatterns) {
        if ($contentText -match $pattern) { return $pattern }
    }
    return $null
}

function Stop-AgentProcess {
    param([System.Diagnostics.Process]$Process, [int]$TimeoutSeconds = 5)
    if ($null -eq $Process -or $Process.HasExited) { return }
    Write-Log "Зупинення процесу (PID: $($Process.Id))..." "WARN"
    try {
        $Process.CloseMainWindow() | Out-Null
        if ($Process.WaitForExit($TimeoutSeconds * 1000)) {
            Write-Log "Процес зупинено м'яко" "SUCCESS"
            return
        }
    } catch { }
    try {
        if (-not $Process.HasExited) {
            Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Write-Log "Процес зупинено примусово" "WARN"
        }
    } catch {
        Write-Log "Не вдалося зупинити процес: $_" "ERROR"
    }
}

function Save-ChatContext {
    param([int]$Lines = 30)
    $sessionFile = Join-Path $Config.WorkingDirectory "AGENT\memories_agent\session\session_$(Get-Date -Format 'yyyy-MM-dd').md"
    if (Test-Path $sessionFile) {
        $contextLines = Get-Content $sessionFile -Tail $Lines -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($contextLines) {
            $contextFile = Join-Path $Config.LogDir "last_context_$(Get-Date -Format 'HHmmss').txt"
            [System.IO.File]::WriteAllText($contextFile, ($contextLines -join "`n"), [System.Text.Encoding]::UTF8)
            Write-Log "Контекст чату збережено: $contextFile" "INFO"
        }
    }
}

function Start-AgentSupervision {
    Write-Log "========================================" "INFO"
    Write-Log "VERCEL SUPERVISOR STARTED" "SUCCESS"
    Write-Log "========================================" "INFO"
    Write-Log "Command: $($Config.Command) $($Config.Arguments -join ' ')" "INFO"
    Write-Log "Working Directory: $($Config.WorkingDirectory)" "INFO"
    Write-Log "Max Restarts: $($Config.MaxRestarts)" "INFO"
    Write-Log "Backoff: $($Config.InitialDelayMs)ms -> $($Config.MaxDelayMs)ms (x$($Config.ExponentialBase))" "INFO"
    Write-Log "========================================" "INFO"

    $restartCount = 0
    $isRunning = $true
    $startTime = Get-Date
    $hookSignalFile = Join-Path $Config.WorkingDirectory "AGENT\state\vercel_restart_signal.json"

    while ($isRunning -and $restartCount -lt $Config.MaxRestarts) {
        $attemptNumber = $restartCount + 1
        Write-Log "--- Запуск агента (спроба $attemptNumber/$($Config.MaxRestarts)) ---" "SUCCESS"

        if (Test-Path $Config.StdErrFile) { Remove-Item $Config.StdErrFile -Force -ErrorAction SilentlyContinue }
        if (Test-Path $hookSignalFile) { Remove-Item $hookSignalFile -Force -ErrorAction SilentlyContinue }

        $process = $null
        $vercelErrorDetected = $false

        try {
            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
            $startInfo.FileName = $Config.Command
            $startInfo.Arguments = ($Config.Arguments -join ' ')
            $startInfo.WorkingDirectory = $Config.WorkingDirectory
            $startInfo.UseShellExecute = $false
            $startInfo.RedirectStandardOutput = $true
            $startInfo.RedirectStandardError = $true
            $startInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
            $startInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8
            $startInfo.CreateNoWindow = $true

            $process = [System.Diagnostics.Process]::Start($startInfo)
            Write-Log "Процес запущено (PID: $($process.Id))" "INFO"

            $stderrTask = $process.StandardError.ReadToEndAsync()
            $checkIntervalMs = 500
            $maxWaitMs = 3600000
            $elapsedMs = 0

            while (-not $process.HasExited -and $elapsedMs -lt $maxWaitMs) {
                Start-Sleep -Milliseconds $checkIntervalMs
                $elapsedMs += $checkIntervalMs

                # Перевіряємо сигнал від хука
                if (Test-Path $hookSignalFile) {
                    try {
                        $signal = Get-Content $hookSignalFile -Raw -Encoding UTF8 | ConvertFrom-Json
                        if ($signal.restartRequested -eq $true) {
                            Write-Log "Отримано сигнал рестарту від хука!" "WARN"
                            $vercelErrorDetected = $true
                            break
                        }
                    } catch { }
                }

                if ($stderrTask.IsCompleted) {
                    $stderrContent = $stderrTask.Result
                    if ($stderrContent) {
                        [System.IO.File]::AppendAllText($Config.StdErrFile, $stderrContent, [System.Text.Encoding]::UTF8)
                        foreach ($pattern in $Config.ErrorPatterns) {
                            if ($stderrContent -match $pattern) {
                                Write-Log "Виявлено помилку Vercel! Патерн: '$pattern'" "ERROR"
                                $vercelErrorDetected = $true
                                break
                            }
                        }
                    }
                    if ($vercelErrorDetected) { break }
                }
            }

            # Якщо процес завершився швидко — перевіряємо stderr після виходу з циклу
            if (-not $vercelErrorDetected -and -not $process.HasExited) {
                $process.WaitForExit(5000) | Out-Null
            }
            if (-not $vercelErrorDetected -and $stderrTask.IsCompleted) {
                $stderrContent = $stderrTask.Result
                if ($stderrContent) {
                    [System.IO.File]::AppendAllText($Config.StdErrFile, $stderrContent, [System.Text.Encoding]::UTF8)
                    foreach ($pattern in $Config.ErrorPatterns) {
                        if ($stderrContent -match $pattern) {
                            Write-Log "Виявлено помилку Vercel! Патерн: '$pattern'" "ERROR"
                            $vercelErrorDetected = $true
                            break
                        }
                    }
                }
            }

        } catch {
            Write-Log "Помилка запуску процесу: $_" "ERROR"
        }

        $vercelErrorPattern = Test-VercelError -LogFilePath $Config.StdErrFile

        if ($vercelErrorDetected -or $vercelErrorPattern) {
            $restartCount++

            if ($restartCount -ge $Config.MaxRestarts) {
                Write-Log "Досягнуто ліміту перезапусків ($($Config.MaxRestarts)). Зупинка." "ERROR"
                $isRunning = $false
                break
            }

            $delay = Get-BackoffDelay -Attempt $restartCount
            $delaySeconds = [Math]::Round($delay / 1000, 1)

            Write-Log "Помилка Vercel AI Gateway виявлена!" "ERROR"
            if ($vercelErrorPattern) { Write-Log "Патерн: $vercelErrorPattern" "ERROR" }
            Write-Log "Наступна спроба через ${delaySeconds}s (attempt $($restartCount + 1))" "WARN"

            Save-ChatContext
            Stop-AgentProcess -Process $process

            Write-Log "Очікування ${delaySeconds}s..." "INFO"
            Start-Sleep -Milliseconds $delay

        } elseif ($process -and $process.HasExited -and $process.ExitCode -eq 0) {
            Write-Log "Агент завершив роботу нормально (ExitCode: 0)" "SUCCESS"
            $isRunning = $false

        } else {
            Write-Log "Невідомий стан процесу. Зупинка." "WARN"
            $isRunning = $false
        }
    }

    $totalTime = (Get-Date) - $startTime
    Write-Log "========================================" "INFO"
    Write-Log "VERCEL SUPERVISOR STOPPED" "INFO"
    Write-Log "Загальний час роботи: $($totalTime.ToString('hh\:mm\:ss'))" "INFO"
    Write-Log "Кількість перезапусків: $restartCount" "INFO"
    Write-Log "========================================" "INFO"

    if ($restartCount -ge $Config.MaxRestarts) {
        Write-Log "УВАГА: Досягнуто ліміту перезапусків. Потрібне ручне втручання!" "ERROR"
        try {
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.MessageBox]::Show(
                "Vercel Supervisor: досягнуто ліміту перезапусків ($($Config.MaxRestarts)).`nПеревірте лог: $($Config.LogFile)",
                "Comfy Agent Supervisor",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Warning
            )
        } catch { }
    }
}

<# ТОЧКА ВХОДУ #>
try {
    Start-AgentSupervision
} catch {
    Write-Log "Критична помилка супервізора: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
} finally {
    Write-Log "Supervisor завершено." "INFO"
}