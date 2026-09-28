# Comfy-smart-lady — Повні інструкції агента

**Версія:** 1.0.0
**Дата останнього оновлення:** 2026-08-20
**Статус:** Стабільний, готовий до синхронізації

---

## 🌸 Ідентичність (найвищий пріоритет)

- **Ім'я:** Comfy-smart-lady
- **Стать:** жіноча
- **Роль:** розумний та обережний coding-агент для локальних та онлайн моделей
- **Пріоритет:** стабільність > структурованість даних > фіксація звітів > швидкість

(Заборонено називати себе GitHub Copilot, Copilot, AI assistant або будь-яким іншим ім'ям).

### Привітання
На привітання: **"Привіт"** чи подібне будь-яке привітання потрібно привітатись, назвати своє ім'я, поточні дату та час. Також назвати які інструкції завантажились та які скрипти працюють.

### Яскрава новина
Знайти якусь яскраву новину в інтернеті та коротко її прокоментувати з тонким почуттям гумору.

---

## 🎯 Головний принцип

**"Шукати реально працюючі механізми роботи коду, шукати варіанти розв'язання в інтернеті, тестувати код запускаючи сервер та аналізуючи код в робочому середовищі. Фіксувати всі події у відповідні журнали. Зберігати базу знань знайденого коду в інтернеті"**

---

## 📦 Структура репозиторію

```
Comfy-smart-lady-agent/                 ← центральне репо (канонічне джерело)
├── README.md                           ← цей файл, опис агента та інструкції встановлення
├── VERSION                             ← версія агента ("1.0.0")
├── .gitignore                          ← ігнорує тимчасові файли (memories/, __pycache__, тощо)
├── CHANGELOG.md                        ← журнал змін
│
├── AGENT/
│   ├── agents/
│   │   └── Comfy-smart-lady.md         ← головний файл інструкцій (канонічний, 169 рядків)
│   ├── skills/                         ← навички агента
│   │   ├── context-management/SKILL.md ← анти-цикл + очищення контексту
│   │   ├── errors/SKILL.md             ← збір даних про помилки агента
│   │   ├── localization-qa/SKILL.md    ← QA локалізації українською
│   │   ├── safe-edit/SKILL.md          ← безпечне редагування файлів
│   │   ├── session-history/SKILL.md    ← історія сесій та журнал дій
│   │   └── small-steps/SKILL.md        ← адаптивна розбивка задач на кроки
│   ├── hooks/
│   │   ├── anti_loop.py                ← детектування циклів (132 рядки, Python 3.12+)
│   │   └── watch_agent_file.py         ← спостереження за файлами (173 рядки)
│   ├── knowledge-base/                 ← база знань агента
│   │   └── README.md
│   ├── memories_agent/                 ← внутрішня пам'ять агента (сесії, помилки, дії)
│   ├── scripts/
│   │   └── generate-agent-catalog.py   ← генератор HTML-каталогу агентів
│   ├── state/                          ← стан анти-циклу
│   ├── templates/                      ← шаблони для stub-файлів
│   └── chats/                          ← документація чатів (README)
│
├── .github/                            ← інструкції для GitHub Copilot (stub-посилання)
│   ├── agents/Comfy-smart-lady.md      ← stub → AGENT/agents/Comfy-smart-lady.md
│   ├── hooks/anti_loop.py              ← синхронізована копія (виконавчий код)
│   ├── knowledge-base/README.md        ← stub → AGENT/knowledge-base/README.md
│   └── skills/                         ← stub-посилання → AGENT/skills/*
│
├── .opencode/                          ← конфігурація OpenCode
│   ├── agents/                         ← stub → AGENT/agents/Comfy-smart-lady.md
│   └── plugin/anti-loop.js             ← JS-плагін антициклу (72 рядки)
│
├── .clinerules/                        ← Cline-правила
│   ├── agents/Comfy-smart-lady.md      ← stub → AGENT/agents/Comfy-smart-lady.md
│   ├── hooks/Loops.json                ← конфігурація anti-loop хука
│   ├── knowledge-base/                 ← stub → AGENT/knowledge-base/README.md
│   ├── scripts/check-ai-co-authors.sh  ← перевірка AI-співавторів
│   └── skills/                        ← stub-посилання → AGENT/skills/*
│
├── .continue/                          ← Continue-конфігурація
│
├── scripts/                            ← інструменти репозиторію (синхронізація та інсталяція)
│   ├── sync-agent.py                   ← основний скрипт синхронізації (261 рядок)
│   ├── install.sh                      ← автоматичне встановлення
│   └── watch_agent_file.py             ← спожитель
│
├── memories/                           ← пам'ять проєкту (сесії, помилки, дії)
│
├── templates/
│   ├── stub_agents.md                  ← шаблон для генерації stub-файлів
│   └── Comfy-smart-lady_*.md            ← бінарні шаблони
│
├── docs/
│   └── agent-sync-plan.md              ← повний план синхронізації
│
├── manifest.json                       ← конфігурація синхронізації (повна)
├── opencode.json                       ← конфігурація OpenCode
└── VERSION
```

---

## 🔧 Ключові скрипти

### `scripts/sync-agent.py` — основний sync-скрипт (261 рядок)
**Функціонал:**
1. Клонує/pull центральне репо у тимчасову папку
2. Копіює файли згідно з manifest.json
3. Створює stub-файли для .opencode/, .clinerules/ (посилаються на AGENT/)
4. Генерує/оновлює шляхи у файлах
5. Робить git status / diff, щоб було видно що змінилось
6. Dry-run режим — показує що зміниться без застосування
7. Backup — створює резервну копію перед змінами
8. Імпотентність — можна запускати багато разів без наслідків

**Передумова:** команди очікують локальний клон центрального репо. Якщо його ще нема:
```bash
git clone https://github.com/ordercomplete/Comfy-smart-lady-agent.git ~/repos/Comfy-smart-lady-agent
```

**Команди:**
```bash
# Встановити в новий проект (копіює конфігурації; ядро AGENT/ скопіюйте окремо або через install.sh)
python sync-agent.py --source ~/repos/Comfy-smart-lady-agent --target .

# Оновити існуючий проект (git pull + копіювання)
python sync-agent.py --update

# Dry-run — показати що зміниться
python sync-agent.py --dry-run

# З pull з центрального репо
python sync-agent.py --pull --apply

# Версія
python sync-agent.py --version
```

> 💡 Для повної установки (ядро AGENT/ + усі конфігурації однією командою) використовуйте `install.sh` / `install.ps1` — див. розділ «Інструкції встановлення».

### `scripts/install.sh` — автоматичне встановлення
**Використання:**
```bash
curl -sL https://raw.githubusercontent.com/ordercomplete/Comfy-smart-lady-agent/main/scripts/install.sh | bash
```

### `scripts/update-manifest.py` — авто-оновлення manifest.json
**Функціонал:**
1. Сканує `AGENT/` (skills, hooks, knowledge-base) і `agent_config/`
2. Генерує секції `files`, `stub_files`, `root_files` у `manifest.json`
3. Нові функціональні файли потрапляють в інсталяцію після його запуску

**Команди:**
```bash
# Показати, як виглядатиме manifest
python agent_config/scripts/update-manifest.py --dry-run

# Перезаписати agent_config/manifest.json
python agent_config/scripts/update-manifest.py --apply
```

---

## 📚 Документація навичок (skills)

### `skills/context-management/SKILL.md`
**Анти-цикл та очищення контексту:**
- Не повторювати думки більше 3 разів поспіль
- 3+ однакові tool call'и — зупинити цикл і змінити підхід
- При 70% заповнення — зберегти поточний прогрес поточної доби `memories/session/session_YYYY-MM-DD.md`
- При 85% — запропонувати новий чат з фіксацією результатів поточного чату

### `skills/errors/SKILL.md`
**Збір даних про роботу Агента (не помилки додатку), взаємодію з інструкціями та правилами під час роботи:**
- Фіксувати цикли та помилки у `memories/errors/error-log_YYYY-MM-DD.md`
- Фіксувати якщо правила заважають виконувати задачу
- Вести журнал дій та помилок для аналізу

### `skills/localization-qa/SKILL.md`
**Перевірка якості української локалізації:**
- Перевіряти переклад на правильність, природність та граматичну коректність
- Формувати питання для перевірки якості локалізації
- Зберігати базу знайдених патернів та рішень

### `skills/safe-edit/SKILL.md`
**Безпечне редагування файлів:**
- Обов'язково читати файл перед edit
- Після edit коротко перевіряти результат
- Перевіряти синтаксис відредагованого файлу
- Не писати нові файли, а редагувати існуючі

### `skills/session-history/SKILL.md`
**Створення та ведення історії сесій, дій та помилок:**
- Створювати файл історії сесії: `memories/session/session_YYYY-MM-DD.md`
- Обов'язково вказувати: дата та час початку, статус "в процесі", основний зміст
- Новий запис завжди додається в кінець файлу
- Кожен запис поточної доби повинен мати поточний час (отриманий через "шаблон отримання поточного часу")

### `skills/small-steps/SKILL.md`
**Адаптивна розбивка задач на кроки:**
- Розбивати задачі залежно від складності (не жорсткі правила, а рекомендації)
- Складні задачі — дрібними кроками
- Прості задачі — більшими блоками

---

## 🎣 Hooks та анти-цикл механізми

### `AGENT/scripts/anti_loop.py` — детектування циклів (132 рядки, Python)

**Детектує:**
- **Exact repeat** — той самий tool на той самий input з cooldown 60 сек
- **Same target loop** — один і той же файл/шлях занадто часто
- **Oscillation** — A-B-A-B патерн чергування дій
- **Tool flood** — надмірне використання одного типу tool
- **No-progress** — багато викликів, але мало унікальних операцій

**Конфігурація:**
```python
WINDOW_SIZE = 24              # кількість останніх викликів для аналізу
EXACT_REPEAT_LIMIT = 8        # точний повтор tool+input
SAME_TARGET_LIMIT = 7         # той самий tool на той самий файл
OSCILLATION_LIMIT = 6         # A-B-A-B патерн
TOOL_FLOOD_LIMIT = 10         # один тип tool підряд
READ_TOOL_FLOOD_LIMIT = 15    # виняток для read_file (дослідження коду)
NO_PROGRESS_WINDOW = 12       # багато викликів з малою кількістю унікальних операцій
MAX_AGE_SECONDS = 1800        # 30 хв — скидання старих даних
RESET_ON_LOOP = True          # при циклі: скинути recent calls і дозволити продовжити
EXACT_REPEAT_COOLDOWN_SECONDS = 60  # запобігає механічним циклам
```

**Результат:**
- При циклі: `allow + reset` (скидає історію, записує в error-log)
- При не циклі: `deny` або `no output` (дозволити без повідомлення)

---

## 🔄 Інструкції встановлення

### Швидка установка в новий проєкт (одна команда)

**Linux / macOS / Git Bash:**
```bash
git clone https://github.com/ordercomplete/Comfy-smart-lady-agent.git /tmp/csl && bash /tmp/csl/scripts/install.sh
```

**Windows PowerShell:**
```powershell
git clone https://github.com/ordercomplete/Comfy-smart-lady-agent.git $env:TEMP\csl; powershell -ExecutionPolicy Bypass -File $env:TEMP\csl\scripts\install.ps1
```

Скрипт автоматично: клонує репо → копіює ядро `AGENT/` → показує dry-run → застосовує синхронізацію → запускає перевірки → прибирає тимчасові файли.

### Ручна установка (покроково)

#### Крок 1: Скопіювати ядро агента
```bash
# Канонічні файли мають бути в проєкті — stub-файли посилаються на них
cp -r Comfy-smart-lady-agent/AGENT ./AGENT        # Linux/macOS
Copy-Item -Recurse ...\AGENT .\AGENT              # Windows PowerShell
```

#### Крок 2: Dry-run синхронізації
```bash
python scripts/sync-agent.py --source ~/repos/Comfy-smart-lady-agent --target . --dry-run
```

#### Крок 3: Застосувати синхронізацію
```bash
python scripts/sync-agent.py --source ~/repos/Comfy-smart-lady-agent --target . --apply
```

#### Крок 4: Додати конфіг OpenCode (опційно)
Скопіюйте `opencode.json` у корінь проєкту — він підключає плагін антициклу та шляхи навичок.

#### Крок 5: Об'єднати .gitignore
Додайте правила з центрального репо: `__pycache__/`, `backup/`, `*.pyc`, runtime-state (`AGENT/state/`, `.github/state/`).

### Оновлення існуючого проєкту
```bash
python scripts/sync-agent.py --pull --apply
```

### Міграція старого проєкту (з дублікатами файлів агента)
Скрипт `migrate-to-central-agent.py` виведено з ужитку 2026-08-28 (міграцію виконано,
копія в `trash/2026-08-28_migrate-to-central-agent.py`).
Для старих проєктів використовуйте `sync-agent.py --pull --apply` вище.

### Перевірка після установки
✅ Всі канонічні файли є в `AGENT/agents/`, `AGENT/skills/`, `AGENT/hooks/`, `.opencode/plugins/`:
- `AGENT/agents/Comfy-smart-lady.md` (169 рядків)
- 6 SKILL.md файлів у `AGENT/skills/*/`
- `AGENT/scripts/anti_loop.py` (132 рядки)
- `.opencode/plugins/anti-loop.js`
- `AGENT/knowledge-base/README.md`

---

## 📊 Таблиця сумісності

| Версія агента | Дата       | Зміни                          | Сумісність з проектами                 |
|---------------|------------|--------------------------------|----------------------------------------|
| 1.0.0         | 2026-08-20 | Початкова версія, повний план   | Усі проекти з .github/ структурою      |

---

## 📝 Ключові відмінності від базового агента

| Фіча              | Базовий агент              | Comfy-smart-lady                                    |
|-------------------|----------------------------|-----------------------------------------------------|
| **Анти-цикл**     | Відсутній                  | Повний механізм з 5 детекторами + автоматичний лог  |
| **Session history**| Обмежена                   | Повна історія сесій із фіксацією всіх подій         |
| **Knowledge base**| Відсутня                   | Структурована база: code-patterns, solutions, external-resources |
| **Sync-скрипти**  | Ручне копіювання           | Автоматична синхронізація через sync-agent.py        |
| **Manifest**      | Відсутній                  | Повний manifest.json з конфігурацією синхронізації   |

---

## 🎯 Додаткові інструменти

### Knowledge Base Solutions
- `.github/knowledge-base/solutions/anti-loop-config.md` — конфігурація анти-циклу
- `.github/knowledge-base/solutions/anti-loop-mechanical-cycles.md` — механізми циклів
- `.github/knowledge-base/solutions/manager-locale-js-loading.md` — завантаження locale JS
- `.github/knowledge-base/solutions/vhs-locale-always-uk.md` — локалізація VHS

### Templates
- `templates/stub_agents.md` — шаблон для генерації stub-файлів (.opencode/agents/, .clinerules/agents/) що посилаються на канонічний файл
- `templates/README_TEMPLATE.md` — шаблон README для проектів

---

## 📄 Ліцензія та посилання

**Центральне репо:** https://github.com/ordercomplete/Comfy-smart-lady-agent.git
**План синхронізації:** `docs/agent-sync-plan.md` (повний план)

**Принцип роботи:**
> "Шукати реально працюючі механізми роботи коду, шукати варіанти розв'язання в інтернеті, тестувати код запускаючи сервер та аналізуючи код в робочому середовищі. Фіксувати всі події у відповідні журнали. Зберігати базу знань знайденого коду в інтернеті"