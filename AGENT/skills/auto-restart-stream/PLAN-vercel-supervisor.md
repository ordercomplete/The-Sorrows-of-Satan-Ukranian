# План реалізації: PowerShell-супервізор для авто-рестарту чату при помилці Vercel AI Gateway

## 1. Загальна концепція

Створити PowerShell-скрипт, який:
- Запускає процес OpenCode (чат з агентом)
- Моніторить stdout/stderr на наявність помилок Vercel AI Gateway
- При виявленні помилки — автоматично перезапускає процес з експоненціальним backoff
- Зберігає лог подій для аналізу
- Має ліміт рестартів щоб уникнути безкінечного циклу

## 2. Файли для створення

| Файл | Призначення |
|------|-------------|
| `AGENT/scripts/vercel-supervisor.ps1` | Основний скрипт-супервізор |
| `AGENT/logs/vercel-supervisor/` | Папка для логів супервізора |

## 3. Архітектура скрипта

### 3.1. Параметри конфігурації

```powershell
$Config = @{
    Command = "opencode"
    Arguments = @("run")
    WorkingDirectory = "D:\GEN\Comfy-smart-lady-agent"
    MaxRestarts = 5
    InitialDelayMs = 3000
    MaxDelayMs = 60000
    ExponentialBase = 2.0
    ErrorPatterns = @(
        "Failed to create stream",
        "inference request failed",
        "failed to invoke model",
        "failed to send request",
        "giving up after \d+ attempt",
        "ai-gateway\.vercel\.sh"
    )
    LogDir = "AGENT\logs\vercel-supervisor"
    LogFile = "supervisor_$(Get-Date -Format 'yyyy-MM-dd').log"
}
```

### 3.2. Алгоритм роботи

1. Ініціалізація: створити лог-папку, записати старт
2. Запуск процесу OpenCode з перехопленням stdout/stderr
3. Моніторинг виводу в реальному часі
4. При виявленні патерну помилки Vercel:
   - Зупинити процес
   - Розрахувати затримку (exponential backoff)
   - Записати в лог
   - Затримка
   - Перезапустити процес
5. При витраченні MaxRestarts — вийти з повідомленням
6. При нормальному завершенні — записати в лог

## 4. Кроки реалізації

| # | Крок | Файл | Оцінка | Статус |
|---|------|------|--------|--------|
| 1 | Створити структуру папок для логів | `AGENT/logs/vercel-supervisor/` | ✅ Зроблено | ✅ |
| 2 | Написати основний скрипт | `AGENT/scripts/vercel-supervisor.ps1` | ✅ Зроблено | ✅ |
| 3 | Додати функцію моніторингу помилок | В основному скрипті | ✅ Зроблено | ✅ |
| 4 | Додати експоненціальний backoff | В основному скрипті | ✅ Зроблено | ✅ |
| 5 | Додати логування з кодуванням UTF-8 | В основному скрипті | ✅ Зроблено | ✅ |
| 6 | Створити `.bat` файл для швидкого запуску | `AGENT/scripts/start-supervisor.bat` | ✅ Зроблено | ✅ |
| 7 | Тестування з симуляцією помилки | — | ✅ Зроблено | ✅ |

## 6. Результати тестування ✅

Тест проведено **31.08.2026 21:40** з тестовим скриптом `test-vercel-error.ps1`, який імітує помилку Vercel.

### Перебіг тесту

```
[SUCCESS] VERCEL SUPERVISOR STARTED
[SUCCESS] --- Запуск агента (спроба 1/3) ---
[INFO] Процес запущено (PID: 32444)
[ERROR] Виявлено помилку Vercel! Патерн: 'Failed to create stream'
[ERROR] Помилка Vercel AI Gateway виявлена!
[WARN] Наступна спроба через 0.5s (attempt 2)
[INFO] Контекст чату збережено: last_context_214100.txt
[SUCCESS] --- Запуск агента (спроба 2/3) ---
[SUCCESS] Агент завершив роботу нормально (ExitCode: 0)
[INFO] VERCEL SUPERVISOR STOPPED
[INFO] Загальний час роботи: 00:00:04
[INFO] Кількість перезапусків: 1
```

### Що перевірено

- ✅ Виявлення помилки Vercel у stderr (патерн `Failed to create stream`)
- ✅ Автоматичний перезапуск процесу з експоненціальним backoff
- ✅ Збереження контексту чату перед рестартом (`last_context_*.txt`)
- ✅ Детектування нормального завершення (ExitCode: 0)
- ✅ Коректне кодування UTF-8 з BOM (script працює в PS 5.1 та PS 7)
- ✅ Логування всіх подій у `supervisor_YYYY-MM-DD.log`

## 7. Файли

| Файл | Статус |
|------|--------|
| `AGENT/scripts/vercel-supervisor.ps1` | ✅ Готовий, протестований |
| `AGENT/scripts/start-supervisor.bat` | ✅ Готовий |
| `AGENT/scripts/test-vercel-error.ps1` | ✅ Тестовий (для перевірки) |
| `AGENT/logs/vercel-supervisor/` | ✅ Папка логів |

## 5. Потенційні проблеми та рішення

| Проблема | Рішення |
|----------|---------|
| Процес не зупиняється одразу | Використати `Stop-Process -Force` через 5 секунд таймауту |
| Помилка виникає знову після рестарту | Ліміт MaxRestarts з повідомленням користувачу |
| Блокування консолі | Можливість запуску через `Start-Process` у прихованому вікні |
