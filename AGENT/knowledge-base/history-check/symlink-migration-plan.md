**Статус: ❌ НЕ РЕАЛІЗОВАНИЙ ПРОЄКТ — міграцію на symlink'и виконано на 0% і відхилено (2026-08-30).**

- Symlink'и так і не були створені: перевірка `AGENT/` і кореня репо показує лише реальні каталоги.
- Архітектуру обрано протилежну: `AGENT/` — канонічне ядро, яке фізично розповсюджується через `manifest.json` (sync-agent.py) у `.github/`, `.clinerules/`, `.continue/`, `.opencode/` (закріплено в v1.4.0, коміт d4052ea).
- Файл структурно дефектний (самопосилання «AGENT/ → AGENT/» замість старих шляхів + артефакти генератора в кінці) — тому як робочий план незастосовний. Зберігається лише як історія рішень.

---


# 📋 План міграції `AGENT/` → `AGENT/` (символічні посилання)

## Мета
Максимальна ефективність при мінімальній кількості записів. Усі файли живуть тільки в `AGENT/`, а `AGENT/` стає symlink-каталогом на `AGENT/`. Це усуває дублювання і робить систему легшою.

---

## 📁 Крок 1 — Перелік усіх файлів у `AGENT/`

```
AGENT/
├── agents/
│   └── Comfy-smart-lady.md               ← головна інструкція агента
├── memories_agent/
│   ├── README.md                         ← опис внутрішньої історії агента
│   ├── session/session_YYYY-MM-DD.md     ← історія внутрішніх сесій агента
│   ├── errors/error-log_YYYY-MM-DD.md    ← помилки та цикли агента
│   ├── actions/action-log_YYYY-MM-DD.md  ← журнал дій агента
│   ├── config-changes/changes_log.md     ← зміни конфігурації
│   ├── cross-reference/external-links.md ← крос-референс до загальних процесів
│   └── migration-note.md                 ← нотатки про міграцію
├── skills/
│   ├── context-management/SKILL.md       ← анти-цикл та очищення контексту
│   ├── session-history/SKILL.md          ← створення і ведення історії сесій
│   ├── errors/SKILL.md                   ← збір даних про роботу агента
│   ├── small-steps/SKILL.md              ← адаптивна розбивка задач на кроки
│   ├── safe-edit/SKILL.md                ← безпечне редагування файлів
│   └── localization-qa/SKILL.md          ← перевірка якості локалізації
├── knowledge-base/
│   ├── README.md                         ← загальний опис бази знань
│   ├── solutions/*.md                    ← готові рішення (anti-loop, патерни)
│   └── code-patterns/*.md                ← шаблони коду
├── hooks/
│   ├── anti_loop.py                      ← головний Python-скрипт анти-loop детекції
│   └── __pycache__/anti_loop.cpython-314.pyc, anti_loop.cpython-312.pyc
├── scripts/
│   └── check-ai-co-authors.sh            ← скрипт перевірки коавторів
├── state/
│   ├── vscode_agent_anti_loop_state.json ← стан анти-loop детекції
│   └── vscode_agent_loop_count.json      ← лічильник циклів
└── agents/Comfy-smart-lady.md            ← копія інструкцій агента (та сама що в .github)

```

---

## 🔗 Крок 2 — Старі посилання в `AGENT/` (що потрібно замінити)

Прочитано ключовий файл інструкцій: **`AGENT/agents/Comfy-smart-lady.md`**

### Посилання, які містяться у файлі:

1. **Лінія 30–32:**
   ```markdown
   - якщо ти .github, то завантажуй `AGENT/hooks/anti_loop.py`
   - якщо ти .opencode, тоді завантажуй спочатку `.opencode/plugin/anti-loop.js` і тільки потім `AGENT/hooks/anti_loop.py`
   - якщо ти .clinerules, тоді завантажуй спочатку `.clinerules/hooks/Loops.json` і тільки потім `AGENT/hooks/anti_loop.py`
   ```

2. **Лінія 40–41:**
   ```markdown
   - `AGENT/memories_agent/` - папки з різними діями агента — внутрішня історія Агента
   - `AGENT/skills/*/SKILL.md` — навички (особливо `session-history/SKILL.md`)
   ```

3. **Лінія 46–47:**
   ```markdown
   - `AGENT/knowledge-base/` — база знань
   ```

4. **Лінія 52–53:**
   ```markdown
   - створюй файл історії сесії Агента: `AGENT/memories_agent/session/session_YYYY-MM-DD.md`
   ```

5. **Лінія 60:**
   ```markdown
   - фіксувати цикли та помилки у `AGENT/memories/errors/error-log_YYYY-MM-DD.md`
   ```

6. **Лінія 74–75:**
   ```markdown
   `AGENT/memories_agent/session/`,
   `AGENT/memories_agent/errors/`,
   `AGENT/memories_agent/actions/`
   ```

7. **Лінія 82–96:** деталізація всіх файлів `memories_agent/`, `errors/`, `actions/`, `config-changes/`, `cross-reference/`

---

## 🛠 Крок 3 — Створення symlink-структури `AGENT/ → AGENT/`

### Структура symlink:

```
AGENT/                          ← тепер це symlink на AGENT/
├── agents/Comfy-smart-lady.md    ────→ AGENT/agents/Comfy-smart-lady.md
├── memories_agent/               ────→ AGENT/memories_agent/ (весь каталог)
│   ├── README.md                 ────→ AGENT/memories_agent/README.md
│   ├── session/session_YYYY-MM-DD.md          → AGENT/memories_agent/session/session_YYYY-MM-DD.md
│   ├── errors/error-log_YYYY-MM-DD.md         → AGENT/memories_agent/errors/error-log_YYYY-MM-DD.md
│   ├── actions/action-log_YYYY-MM-DD.md       → AGENT/memories_agent/actions/action-log_YYYY-MM-DD.md
│   ├── config-changes/changes_log.md          → AGENT/memories_agent/config-changes/changes_log.md
│   └── cross-reference/external-links.md      → AGENT/memories_agent/cross-reference/external-links.md
├── skills/                       ────→ AGENT/skills/ (весь каталог)
│   ├── context-management/SKILL.md          → AGENT/skills/context-management/SKILL.md
│   ├── session-history/SKILL.md             → AGENT/skills/session-history/SKILL.md
│   ├── errors/SKILL.md                      → AGENT/skills/errors/SKILL.md
│   ├── small-steps/SKILL.md                 → AGENT/skills/small-steps/SKILL.md
│   ├── safe-edit/SKILL.md                   → AGENT/skills/safe-edit/SKILL.md
│   └── localization-qa/SKILL.md             → AGENT/skills/localization-qa/SKILL.md
├── knowledge-base/               ────→ AGENT/knowledge-base/ (весь каталог)
│   ├── README.md                          → AGENT/knowledge-base/README.md
│   ├── solutions/*.md                     → AGENT/knowledge-base/solutions/*.md
│   └── code-patterns/*.md                 → AGENT/knowledge-base/code-patterns/*.md
├── hooks/                        ────→ AGENT/hooks/ (весь каталог)
│   ├── anti_loop.py                       → AGENT/hooks/anti_loop.py
│   └── __pycache__/                       → AGENT/hooks/__pycache__/
├── state/                        ────→ AGENT/state/ (весь каталог)
│   ├── vscode_agent_anti_loop_state.json  → AGENT/state/vscode_agent_anti_loop_state.json
│   └── vscode_agent_loop_count.json       → AGENT/state/vscode_agent_loop_count.json
└── scripts/                      ────→ AGENT/scripts/ (весь каталог)
    └── check-ai-co-authors.sh             → AGENT/scripts/check-ai-co-authors.sh

```

---

## 📊 Крок 4 — Таблиця замін посилань

| № | Старий шлях (AGENT/) | Новий шлях (AGENT/) | Тип заміни | Файл де змінювати |
|---|------------------------|---------------------|------------|-------------------|
| 1 | `AGENT/hooks/anti_loop.py` | `AGENT/hooks/anti_loop.py` | symlink | `AGENT/agents/Comfy-smart-lady.md` лінії 30–32 |
| 2 | `AGENT/memories_agent/` | `AGENT/memories_agent/` | symlink каталогу | `AGENT/agents/Comfy-smart-lady.md` лінія 40, 52–53, 74–96 |
| 3 | `AGENT/skills/context-management/SKILL.md` | `AGENT/skills/context-management/SKILL.md` | symlink файлу | `AGENT/agents/Comfy-smart-lady.md` лінія 127 (розділ анти-цикл) |
| 4 | `AGENT/skills/session-history/SKILL.md` | `AGENT/skills/session-history/SKILL.md` | symlink файлу | `AGENT/agents/Comfy-smart-lady.md` лінії 41, 57, 82–96 |
| 5 | `AGENT/knowledge-base/` | `AGENT/knowledge-base/` | symlink каталогу | `AGENT/agents/Comfy-smart-lady.md` лінія 47 |
| 6 | `AGENT/memories/errors/error-log_YYYY-MM-DD.md` | `AGENT/memories_agent/errors/error-log_YYYY-MM-DD.md` | symlink файлу + перенесення в memories_agent | `AGENT/agents/Comfy-smart-lady.md` лінія 60 |
| 7 | `AGENT/skills/small-steps/SKILL.md` | `AGENT/skills/small-steps/SKILL.md` | symlink файлу | `AGENT/agents/Comfy-smart-lady.md` лінії 10, 28–31 |
| 8 | `AGENT/skills/errors/SKILL.md` | `AGENT/skills/errors/SKILL.md` | symlink файлу | `AGENT/agents/Comfy-smart-lady.md` лінія 9 |
| 9 | `AGENT/skills/localization-qa/SKILL.md` | `AGENT/skills/localization-qa/SKILL.md` | symlink файлу | `AGENT/agents/Comfy-smart-lady.md` лінія 10, 28–31 |
| 10 | `AGENT/skills/safe-edit/SKILL.md` | `AGENT/skills/safe-edit/SKILL.md` | symlink файлу | `AGENT/agents/Comfy-smart-lady.md` лінії 10, 28–31 |

---

## 📄 Крок 5 — Додаткові файли для оновлення посилань

Окрім `AGENT/agents/Comfy-smart-lady.md`, також перевірити й оновити:

| Файл | Посилання де змінювати |
|------|------------------------|
| `AGENT/skills/session-history/SKILL.md` | Всі посилання на `AGENT/memories_agent/*`, `AGENT/knowledge-base/*` → замінити на `AGENT/` |
| `AGENT/memories_agent/README.md` | Усередині файлу всі шляхи вже правильні, але якщо є посилання на `AGENT/...` — змінити на `AGENT/...` |
| `AGENT/knowledge-base/solutions/*.md` | Перевірити посилання на інші файли (якщо є) і замінити шляхи на `AGENT/` |

---

## 🛠 Крок 6 — Як створити symlink-структуру

```powershell
# Створення символічних посилань для кожного підкаталогу:

New-Item -ItemType SymbolicLink -Path ".github\agents" -Target "AGENT\agents"
New-Item -ItemType SymbolicLink -Path ".github\memories_agent" -Target "AGENT\memories_agent"
New-Item -ItemType SymbolicLink -Path ".github\skills" -Target "AGENT\skills"
New-Item -ItemType SymbolicLink -Path ".github\knowledge-base" -Target "AGENT\knowledge-base"
New-Item -ItemType SymbolicLink -Path ".github\hooks" -Target "AGENT\hooks"
New-Item -ItemType SymbolicLink -Path ".github\state" -Target "AGENT\state"
New-Item -ItemType SymbolicLink -Path ".github\scripts" -Target "AGENT\scripts"

# Перевірка:
Get-ChildItem .github | Format-Table Name, LinkType, TargetPath
```

---

## ✏️ Крок 7 — Оновлення `AGENT/agents/Comfy-smart-lady.md` (головний файл інструкцій)

**Замінити всі посилання:**

**До:**
```markdown
- `AGENT/hooks/anti_loop.py`
- `AGENT/memories_agent/session/session_YYYY-MM-DD.md`
- `AGENT/skills/context-management/SKILL.md`
- `AGENT/knowledge-base/`
```

**Після:**
```markdown
- `AGENT/hooks/anti_loop.py`
- `AGENT/memories_agent/session/session_YYYY-MM-DD.md`
- `AGENT/skills/context-management/SKILL.md`
- `AGENT/knowledge-base/`
```

---

## ✅ Крок 8 — Фінальна структура після заміни

```
AGENT/                          ← ОРИГІНАЛЬНІ ФАЙЛИ (джерело)
├── agents/Comfy-smart-lady.md
├── memories_agent/
│   ├── README.md
│   ├── session/session_YYYY-MM-DD.md
│   ├── errors/error-log_YYYY-MM-DD.md
│   └── actions/action-log_YYYY-MM-DD.md
├── skills/*/SKILL.md
├── knowledge-base/solutions/*.md
├── hooks/anti_loop.py
├── state/vscode_agent_anti_loop_state.json
└── scripts/check-ai-co-authors.sh

AGENT/                         ← SYMLINK на AGENT/ (тільки посилання!)
├── agents → AGENT\agents
├── memories_agent → AGENT\memories_agent
├── skills → AGENT\skills
├── knowledge-base → AGENT\knowledge-base
├── hooks → AGENT\hooks
├── state → AGENT\state
└── scripts → AGENT\scripts

```

---

## 🧭 Крок 9 — Крос-референс з `memories/` (загальні процеси проекту)

Кожен чат у `chats/[chat_ID]/` може мати посилання на:
- `AGENT/memories/session/session_YYYY-MM-DD.md` → `AGENT/memories/session/session_YYYY-MM-DD.md`
- `AGENT/memories/errors/error-log_YYYY-MM-DD.md` → `AGENT/memories/errors/error-log_YYYY-MM-DD.md`
- `AGENT/memories/actions/action-log_YYYY-MM-DD.md` → `AGENT/memories/actions/action-log_YYYY-MM-DD.md`

---

## 🏁 Крок 10 — Чек-ліст виконання

### Етап 1: Створення symlink'ів
- [ ] Створити symlink для `AGENT/agents` → `AGENT/agents`
- [ ] Створити symlink для `AGENT/memories_agent` → `AGENT/memories_agent`
- [ ] Створити symlink для `AGENT/skills` → `AGENT/skills`
- [ ] Створити symlink для `AGENT/knowledge-base` → `AGENT/knowledge-base`
- [ ] Створити symlink для `AGENT/hooks` → `AGENT/hooks`
- [ ] Створити symlink для `AGENT/state` → `AGENT/state`
- [ ] Створити symlink для `AGENT/scripts` → `AGENT/scripts`

### Етап 2: Оновлення інструкцій у `AGENT/agents/Comfy-smart-lady.md`
- [ ] Замінити `AGENT/hooks/anti_loop.py` → `AGENT/hooks/anti_loop.py` (лінії 30–32)
- [ ] Замінити `AGENT/memories_agent/` → `AGENT/memories_agent/` (лінія 40, 52–53, 74–96)
- [ ] Замінити `AGENT/skills/context-management/SKILL.md` → `AGENT/skills/context-management/SKILL.md` (лінія 127)
- [ ] Замінити `AGENT/knowledge-base/` → `AGENT/knowledge-base/` (лінія 46–47)
- [ ] Замінити `AGENT/memories/errors/error-log_YYYY-MM-DD.md` → `AGENT/memories_agent/errors/error-log_YYYY-MM-DD.md` (лінія 60)
- [ ] Перевірити всі посилання на інші SKILL.md файли

### Етап 3: Оновлення інших файлів
- [ ] Оновити `AGENT/skills/session-history/SKILL.md` — замінити всі `AGENT/...` на `AGENT/...`
- [ ] Перевірити `AGENT/memories_agent/README.md` на наявність старих посилань
- [ ] Перевірити `AGENT/knowledge-base/solutions/*.md` на наявність старих посилань

### Етап 4: Верифікація
- [ ] Протестувати symlink'і — чи читаються файли через `AGENT/` коректно
- [ ] Запустити анти-loop скрипт і перевірити що він знаходить `AGENT/scripts/anti_loop.py`
- [ ] Перевірити чи створюється сесійний лог у `AGENT/memories_agent/session/session_YYYY-MM-DD.md` через symlink `AGENT/...`

---

## 📝 Крок 11 — Примітки до міграції

- **Чому symlink, а не копіювання?** Symlink усуває дублювання файлів — всі зміни в `AGENT/` автоматично відбиваються у `AGENT/`. Це зберігає місце і спрощує підтримку.

- **Що робити зі старими копіями файлів?** Після успішної міграції можна видалити дублікати в `AGENT/` (вони автоматично перетворяться на symlink'і, якщо `New-Item -ItemType SymbolicLink` спрацює коректно).

- **Переваги системи:**
  - ✅ Мінімум записів — всі файли в одній папці `AGENT/`
  - ✅ Максимальна ефективність — нема дублювання коду і інструкцій
  - ✅ Легше підтримувати — зміни в одній точці оновлюють усю систему
  - ✅ Чиста архітектура — `AGENT/` стає "прозорою оболонкою" на `AGENT/`

</content>
<parameter=filePath>
D:\GEN\Comfy-smart-lady-agent\AGENT\memories_agent\symlink-migration-plan.md
