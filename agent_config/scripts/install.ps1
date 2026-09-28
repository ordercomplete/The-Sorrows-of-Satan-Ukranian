# install.ps1 — Повна установка Comfy-smart-lady-agent у поточний проєкт (Windows).
#
# Використання:
#   powershell -ExecutionPolicy Bypass -File scripts\install.ps1 [URL_репозиторію]
#
# Що робить:
#   1. Клонує центральне репо у тимчасову папку
#   2. Копіює канонічне ядро AGENT/ у цільовий проєкт
#   3. Показує dry-run синхронізації
#   4. Застосовує синхронізацію (.github/, .clinerules/, .opencode/)
#   5. Запускає перевірки (py_compile)
#   6. Прибирає тимчасові файли

param(
    [string]$RepoUrl = "https://github.com/ordercomplete/Comfy-smart-lady-agent.git"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$TargetDir = "."
$TmpDir = Join-Path $env:TEMP ("csl_install_" + [guid]::NewGuid().ToString("N").Substring(0,8))

Write-Host "🚀 Інсталяція Comfy-smart-lady-agent..." -ForegroundColor Cyan
Write-Host "   Джерело: $RepoUrl"
Write-Host "   Цільова директорія: $(Get-Location)"

# Перевірка залежностей
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Host "❌ git не знайдено" -ForegroundColor Red; exit 1 }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Write-Host "❌ python не знайдено" -ForegroundColor Red; exit 1 }

try {
    # 1. Клонувати центральне репо
    Write-Host ""
    Write-Host "📥 Крок 1/5: Клонування центрального репозиторію..."
    git clone --depth 1 $RepoUrl $TmpDir
    if ($LASTEXITCODE -ne 0) { throw "git clone завершився з помилкою" }

    # 2. Ядро AGENT/ тепер розгортає sync-agent.py --apply (Крок 4), тож тут не дублюємо.
    Write-Host ""
    Write-Host "📦 Крок 2/5: Ядро AGENT/ буде розгорнуто синхронізацією (Крок 4)..."

    # 3. Dry-run
    Write-Host ""
    Write-Host "🔍 Крок 3/5: Dry-run синхронізації..."
    python (Join-Path $TmpDir "agent_config\scripts\sync-agent.py") --source $TmpDir --target $TargetDir --dry-run

    # 4. Застосувати
    Write-Host ""
    Write-Host "⚙️  Крок 4/5: Застосування синхронізації..."
        python (Join-Path $TmpDir "agent_config\scripts\sync-agent.py") --source $TmpDir --target $TargetDir --apply

    # 4.5. Перейменовуємо memories -> memories_{project_root} (ідемпотентно)
    Write-Host "   🗂️  namespacing memories/ -> memories_{project_root} ..."
    python "$TargetDir\AGENT\scripts\rename_memories.py"

    # 5. Перевірки
    Write-Host ""
    Write-Host "🧪 Крок 5/5: Перевірка встановлення..."
    python -m py_compile .\AGENT\scripts\anti_loop.py .\AGENT\scripts\watch_agent_file.py .\AGENT\scripts\str.translate.py
    if ($LASTEXITCODE -eq 0) { Write-Host "   ✅ core скрипти компілюються (AGENT/scripts)" }
    if (Test-Path ".\AGENT\scripts\anti_loop.py") { Write-Host "   ✅ AGENT/scripts/anti_loop.py на місці" }
    if (Test-Path ".\.clinerules\hooks\Loops.json") { Write-Host "   ✅ .clinerules/hooks/Loops.json на місці" }
    if (-not (Test-Path ".\.opencode\plugins\anti-loop.js")) {
        Write-Host "   ⚠️  .opencode/plugins/anti-loop.js відсутній (скопіюйте вручну)" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ .opencode/plugins/anti-loop.js на місці"
    }

    # Додаткова перевірка (крок 5/5): agent-lock.json та команда status
    if (Test-Path ".\agent-lock.json") {
        Write-Host "   ✅ agent-lock.json створено"
    } else {
        Write-Host "   ⚠️  agent-lock.json відсутній" -ForegroundColor Yellow
    }
    Write-Host "   📋 Стан Агента (sync-agent.py status):"
    python .\agent_config\scripts\sync-agent.py status

    Write-Host ""
    Write-Host "✅ Успішно встановлено!" -ForegroundColor Green
    Write-Host "   Наступні кроки:"
    Write-Host "   - Додайте opencode.json у корінь проєкту (якщо використовуєте OpenCode)"
    Write-Host "   - Об'єднайте .gitignore з правилами центрального репо"
}
finally {
    # Прибрати тимчасову папку
    if (Test-Path $TmpDir) {
        Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
    }
}
