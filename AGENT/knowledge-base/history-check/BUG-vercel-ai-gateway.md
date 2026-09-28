# BUG: Vercel AI Gateway Stream Error — Автоматичний рестарт чату

**Дата виявлення:** 2026-08-31
**Статус:** Вирішено ✅
**Серйозність:** Висока (блокує роботу агента)

---

## Опис проблеми

При роботі з моделлю `private/longcat-2.0` через Vercel AI Gateway періодично виникає помилка:

```
Failed to create stream: inference request failed: failed to generate stream from Vercel: 
failed to invoke model 'private/longcat-2.0' with streaming: failed to send request: 
POST https://ai-gateway.vercel.sh/v1/chat/completions giving up after 4 attempt(s)
```

**Вплив:** Чат повністю вмирає, поточна сесія втрачається, користувач має вручну починати новий чат.

**Причина:** Проблеми на стороні Vercel AI Gateway або мережеві збої. Не пов'язано з кодом агента.

---

## Архітектуя рішення

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    АВТОМАТИЧНИЙ РЕСТАРТ ЧАТУ                           │
│                                                                         │
│  ┌──────────────┐    сигнал    ┌──────────────────┐                    │
│  │  Hook        │ ───────────> │  Supervisor       │                    │
│  │  (всередині  │   write     │  (зовнішній       │                    │
│  │   чату)      │   signal    │   процес)         │                    │
│  └──────────────┘             └──────────────────┘                    │
│        │                              │                                │
│        │ виявляє помилку              │ моніторить stderr              │
│        │ пише сигнал                  │ читає signal file              │
│        │                              │ перезапускає процес            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Потік роботи:

1. **Хук** `vercel_error_tracker.py` перехоплює виклики інструментів
2. При виявленні помилки Vercel → пише сигнал у `AGENT/state/vercel_restart_signal.json`
3. **Супервізор** `vercel-supervisor.ps1` моніторить:
   - stderr процесу на патерни Vercel
   - файл сигналу від хука
4. При виявленні → зупиняє процес → чекає (backoff) → перезапускає

---

## Результати тестування інтеграції ✅

### Тест 1: Supervisor виявляє помилку в stderr

```
[SUCCESS] Запуск агента (спроба 1/2)
[INFO] Процес запущено (PID: 41096)
[ERROR] Виявлено помилку Vercel! Патерн: 'Failed to create stream'
[WARN] Наступна спроба через 0.5s (attempt 2)
[SUCCESS] Запуск агента (спроба 2/2)
[ERROR] Досягнуто ліміту перезапусків (2). Зупинка.
```

### Тест 2: Supervisor отримує сигнал від хука

```
[SUCCESS] Запуск агента (спроба 1/2)
[INFO] Процес запущено (PID: 42652)
[WARN] Отримано сигнал рестарту від хука!
[ERROR] Помилка Vercel AI Gateway виявлена!
[WARN] Наступна спроба через 0.5s (attempt 2)
[INFO] Контекст чату збережено
[WARN] Зупинення процесу (PID: 42652)...
[SUCCESS] Процес зупинено м'яко
[SUCCESS] Запуск агента (спроба 2/2)
[INFO] Процес запущено (PID: 28064)
[SUCCESS] Агент завершив роботу нормально (ExitCode: 0)
[INFO] Кількість перезапусків: 1
```

### Що підтверджено:

- ✅ Хук виявляє помилку Vercel і пише сигнал
- ✅ Супервізор детектує сигнал від хука
- ✅ Супервізор зупиняє процес і перезапускає
- ✅ Контекст чату зберігається перед рестартом
- ✅ Експоненціальний backoff працює
- ✅ Ліміт рестартів працює

### 1. PowerShell-супервізор (зовнішній моніторинг)

**Файл:** `AGENT/scripts/vercel-supervisor.ps1`

Запускається окремо перед стартом чату. Моніторить процес агента і автоматично перезапускає його при виявленні помилки Vercel.

**Можливості:**
- Моніторинг stderr у реальному часі на 7 патернів помилок
- Експоненціальний backoff (3с → 6с → 12с → ...)
- Збереження контексту чату перед рестартом
- Логування всіх подій у UTF-8
- Налаштовуваний ліміт рестартів (за замовчуванням 5)

**Запуск:**
```powershell
.\AGENT\scripts\start-supervisor.bat
# Або:
powershell -File AGENT\scripts\vercel-supervisor.ps1 -MaxRestarts 5 -InitialDelayMs 3000
```

### 2. Python-хук (вбудований моніторинг)

**Файл:** `AGENT/scripts/vercel_error_tracker.py`

Працює за паттерном `anti_loop.py`. Перехоплює виклики інструментів і перевіряє їх на наявність помилок Vercel.

**Можливості:**
- Відстідковує послідовні помилки Vercel
- Рахує кількість помилок у вікні 5 хвилин
- При досягненні порогу (3 помилки) — логує подію і повертає алерт
- Зберігає стан у `AGENT/state/vscode_agent_vercel_error_state.json`

---

## Структура файлів

```
AGENT/
├── hooks/
│   └── vercel_error_tracker.py      # Хук для виявлення помилок
├── scripts/
│   ├── vercel-supervisor.ps1        # PowerShell-супервізор
│   ├── start-supervisor.bat         # Швидкий запуск
│   └── test-vercel-error.ps1        # Тестовий скрипт
├── memories_agent/
│   └── logs/
│       └── vercel-supervisor/       # Логи супервізора
│           ├── supervisor_YYYY-MM-DD.log
│           └── last_context_*.txt   # Контекст перед рестартом
└── knowledge-base/
    └── history-check/
        └── BUG-vercel-ai-gateway.md # Цей файл
```

---

## Як користуватись

### Для проактивного захисту:
1. Запусти `start-supervisor.bat` перед початком роботи
2. Супервізор автоматично рестартує при падінні

### Для діагностики:
1. Перевір `AGENT/memories_agent/logs/vercel-supervisor/supervisor_*.log`
2. Перевір `AGENT/memories_agent/errors/error-log_*.md` (секція Vercel Error)

### Для тестування:
```powershell
powershell -File AGENT\scripts\test-vercel-error.ps1
```

---

## Результати тестування

```
Спроба 1: ❌ Vercel error виявлена → рестарт (backoff 0.5s)
Спроба 2: ✅ Агент завершився нормально (ExitCode: 0)
Час: 4 сек, 1 перезапуск
```

---

## Пов'язані файли

- `AGENT/skills/auto-restart-stream/SKILL.md` — план реалізації (3 варіанти)
- `AGENT/skills/auto-restart-stream/PLAN-vercel-supervisor.md` — детальний план супервізора
- `.opencode/src/utils/AutoRestartStreamClient.ts` — TypeScript-обгортка для SSE-потоку (Варіант 1)
- `.opencode/src/client.ts` — Інтеграція з Vercel AI Gateway

---

## Примітки

- Супервізор — це **зовнішній** скрипт, він не може перезапустити чат зсередини
- Хук `vercel_error_tracker.py` працює на рівні інструментів, але може не побачити помилку стріму (вона відбувається на рівні API)
- Надійний захист — комбінація обох механізмів + запуск супервізора перед роботой
