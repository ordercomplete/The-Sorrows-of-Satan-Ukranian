# CHANGELOG — Comfy-smart-lady-agent

## Версія 1.4.0 (2026-08-30) — agent-lock.json закрито (BUG-agent-lock.md, Варіант Б)

### 🔒 Команди `status` / `remove` / `gitignore` на основі `agent-lock.json`
- Після `sync-agent.py --apply` у корені цільового проєкту створюється
  `agent-lock.json`, що фіксує всі встановлені файли Агента за типами
  (`copy_full` / `stub` / `root_files`) з хешами.
- Додано підкоманди:
  - `sync-agent.py status [--verbose]` — OK / Modified / Missing / New;
  - `sync-agent.py remove [--force]` — видалення ЛИШЕ Agent-файлів;
  - `sync-agent.py gitignore` — гарантує локальні `.gitignore` папок Агента.

### 🚮 Видалення через Корзину
- `remove` більше не робить безповоротне `unlink()`: файли переносяться
  у Корзину через `delete_to_trash.py` (AGENT/* → `AGENT/trash/`,
  решта → `trash/`) з маршрутизацією за коренем таргету.

### 🧹 Політика `.gitignore`
- `--apply` і `remove` більше НЕ змінюють кореневий `.gitignore`
  цільового проєкту (відповідно до Частини I §2). Ігнор-правила живуть
  у локальних `.gitignore` папок Агента.
- З центрального репо прибрано випадково закомічений `agent-lock.json`
  та артефакти `__pycache__`/`*.pyc`; додано `agent-lock.json` до ігнор.

### 🧪 Тестування та документи
- Відновлено активний `test_install.ps1` (перевірки lock/status/gitignore).
- Оновлено `Install_Comfy-smart-lady-agent.txt` §2, `SCRIPTS_CATALOG.md`,
  docstring `sync-agent.py`, кроки перевірки в `install.sh` / `install.ps1`.

---

### 🎯 Основні зміни (керівництво: `INTEGRATION_PLAN_V3.md`)

#### 🔀 Зміни розташування файлів (manifest.json)
- **`opencode.json` ЗАЛИШАЄТЬСЯ В КОРЕНІ** — конфігураційний файл LM Studio Code, його правила очікують файл саме у корені. Більше не чіпаємо.
- Всі інші конфліктні файли ізольовані в `agent_config/`: `.gitignore`, `README.md`, `CHANGELOG.md`, `VERSION`, `manifest.json`, `Install_*.txt`, `docs/*`, `scripts/*`, `templates/*`, `.continue/*`.
- `manifest.json` тепер єдине джерело правди для розташування файлів (секція `root_files`).

#### 🔄 Оновлені скрипти
- `sync-agent.py` (v1.2.0): шукає `agent_config/manifest.json`, а не кореневий `manifest.json`.
- `install.ps1` / `install.sh`: викликають `agent_config/scripts/sync-agent.py`.
- `test_install.ps1`: переписано без жорстких шляхів (використовує `$PSScriptRoot`).

#### 🗑️ Корзина видалених файлів
- Створено `agent_config/trash/` з лог-файлом `deletion_log.md`, який фіксує всі видалення/переміщення файлів під час інтеграції.

#### 📄 Документація
- Створено `INTEGRATION_PLAN_V3.md` — актуальний план безконфліктної інтеграції з поточним станом.

---

### 🎯 Основні зміни

#### ✅ Канонічні файли агента
- **`agents/Comfy-smart-lady.md`** — головний файл інструкцій (103 рядки)
  - Ідентичність: жіноча, розумний та обережний coding-агент
  - Привітання з поточним часом, іменем, завантаженими інструкціями
  - Яскрава новина в інтернеті з тонким почуттям гумору
  - Головний принцип роботи: пошук реальних механізмів, тестування коду, фіксація подій

#### ✅ Навички (skills) — повні файли SKILL.md
1. **`skills/context-management/SKILL.md`**
   - Анти-цикл та очищення контексту
   - Правило: не повторювати думки більше 3 разів поспіль
   - При 70% заповнення — зберегти поточний прогрес `memories/session/session_YYYY-MM-DD.md`
   - При 85% — запропонувати новий чат

2. **`skills/errors/SKILL.md`**
   - Збір даних про роботу Агента (не помилки додатку)
   - Взаємодія з інструкціями та правилами під час роботи
   - Фіксація циклів та помилок у `memories/errors/error-log_YYYY-MM-DD.md`

3. **`skills/localization-qa/SKILL.md`**
   - Перевірка якості української локалізації
   - Формування питань для перевірки якості перекладу
   - Збереження бази знайдених патернів та рішень

4. **`skills/safe-edit/SKILL.md`**
   - Безпечне редагування файлів
   - Обов'язкове читання перед edit, перевірка синтаксису після
   - Пріоритет: read > grep > list перед write

5. **`skills/session-history/SKILL.md`**
   - Створення та ведення історії сесій, дій та помилок
   - Файл `memories/session/session_YYYY-MM-DD.md` з обов'язковим зазначенням часу через "шаблон отримання поточного часу"
   - Нові записи додаються в кінець файлу

6. **`skills/small-steps/SKILL.md`**
   - Адаптивна розбивка задач на кроки залежно від складності
   - Не жорсткі правила, а рекомендації

#### ✅ Анти-цикл механізм
- **`.github/hooks/anti_loop.py`** — Python-скрипт детектування циклів (317 рядків)
  - Діагностує: exact repeat, same target, oscillation, tool flood, no-progress
  - Конфігурація: WINDOW_SIZE=24, EXACT_REPEAT_LIMIT=8, SAME_TARGET_LIMIT=7, OSCILLATION_LIMIT=6, TOOL_FLOOD_LIMIT=10, READ_TOOL_FLOOD_LIMIT=15, NO_PROGRESS_WINDOW=12, MAX_AGE_SECONDS=1800
  - Автоматичний запис циклів у `memories/errors/error-log_YYYY-MM-DD.md`
  - Cooldown між спрацюваннями: 60 секунд

- **`.opencode/plugin/anti-loop.js`** — JS-плагін для OpenCode

#### ✅ База знань
- **`.github/knowledge-base/README.md`** — структура бази знань, як користуватись
- **`.github/knowledge-base/solutions/`**:
  - `anti-loop-config.md` — конфігурація анти-циклу
  - `anti-loop-mechanical-cycles.md` — механізми циклів
  - `manager-locale-js-loading.md` — завантаження locale JS
  - `vhs-locale-always-uk.md` — локалізація VHS

#### ✅ Синхронізаційні інструменти
- **`scripts/sync-agent.py`** (9041 рядків) — основний sync-скрипт:
  - Клонувати/pull центральне репо у тимчасову папку
  - Копіювати файли згідно з manifest.json
  - Створювати stub-файли для .opencode/, .clinerules/
  - Генерувати/оновлювати шляхи у файлах
  - Робити git status / diff
  - Dry-run режим, backup, імпотентність

- **`scripts/install.sh`** (833 байти) — автоматичне встановлення:
  ```bash
  curl -sL https://raw.githubusercontent.com/ordercomplete/Comfy-smart-lady-agent/main/scripts/install.sh | bash
  ```

- **`scripts/migrate-to-central-agent.py`** (10625 рядків) — міграція з поточних дублікатів:
  - Зібрати всі актуальні файли з `.github/`, `.opencode/`, `.clinerules/`
  - Класти їх у правильну структуру нового репо
  - Видалити дублікати з проекту (або замінити на stub)
  - Створити manifest.json для поточного стану

#### ✅ Конфігурація та шаблони
- **`manifest.json`** — повна конфігурація синхронізації:
  ```json
  {
    "version": "1.0.0",
    "agent_name": "Comfy-smart-lady",
    "description": "Центральний репозиторій для агента Comfy-smart-lady",
    "files": { ... },
    "stub_files": { ... },
    "directories_to_create": [ ... ],
    "post_sync": { ... }
  }
  ```

- **`templates/stub_agents.md`** — шаблон для генерації stub-файлів (.opencode/agents/, .clinerules/agents/) що посилаються на канонічний файл

#### ✅ Документація та план
- **`docs/agent-sync-plan.md`** (687 рядків) — повний план синхронізації агент-репозиторію:
  - Повний аналіз поточної структури файлів з таблицями дублікатів та статусом
  - Кількісна оцінка всіх файлів (103 рядки агента, 279 рядків anti_loop.py)
  - Структура центрального репозиторію з детальними шляхами
  - Синхронізація для: .github/, .opencode/, .clinerules/
  - Порядок дій (кроки 1-6) від структури до фінальної документації
  - Детальні описи синхронізації, stub-файлів, sync-agent.py, migrate-to-central-agent.py
  - Таблиця сумісності та рекомендації

### 🔧 Інші інструменти
- **`.github/scripts/check-ai-co-authors.sh`** — скрипт перевірки AI commit'ів
- **VERSION** — "1.0.0"
- **.gitignore** — ігнорує тимчасові файли (memories/, __pycache__, тощо)

### 📊 Порівняння з базовим агентом

| Фіча              | Базовий агент              | Comfy-smart-lady                                    |
|-------------------|----------------------------|-----------------------------------------------------|
| **Анти-цикл**     | Відсутній                  | Повний механізм з 5 детекторами + автоматичний лог  |
| **Session history**| Обмежена                   | Повна історія сесій із фіксацією всіх подій         |
| **Knowledge base**| Відсутня                   | Структурована база: code-patterns, solutions, external-resources |
| **Sync-скрипти**  | Ручне копіювання           | Автоматична синхронізація через sync-agent.py        |
| **Manifest**      | Відсутній                  | Повний manifest.json з конфігурацією синхронізації   |

### 🎯 Головні принципи роботи агента

1. **Перевіряє поточну дату та час:** "шаблон отримання поточного часу"
2. **Завантажує потрібні файли скриптів** залежно від чату:
   - `.github/` → `.github/hooks/anti_loop.py`
   - `.opencode/` → `.opencode/plugin/anti-loop.js`, потім `.github/hooks/anti_loop.py`
   - `.clinerules/` → `.clinerules/hooks/Loops.json`, потим `.github/hooks/anti_loop.py`
3. **Завжди читає файли проекту перед початком:**
   - `docs/README.md` — огляд, структура, документація
   - `memories/session/` — історія сесій
   - `.github/skills/*/SKILL.md` — навички (особливо session-history)
   - `PLAN_and_INSTRUCTION/` — плани та інструкції
   - `copilot-instructions.md`, `.instructions.md` — користувацькі інструкції
4. **Завантажує знання з бази:**
   - `.github/knowledge-base/README.md` — структура, як користуватись
   - `.github/knowledge-base/code-patterns/*.md` — патерни коду ComfyUI
   - `.github/knowledge-base/solutions/*.md` — знайдені рішення проблем
   - `.github/knowledge-base/external-resources/*.md` — корисні посилання з поясненням

### 📝 Стиль відповідності агента

**Складні дії (редагування файлів, запуск команд):**
```
**Думаю про те як я: ...** [коротке міркування, 1-3 речення]
**Виконую ось це: ...** [що роблю зараз]
```

**Простий діалог:** Говори природно — як звичайна людина в розмові з іншою людиною.

**Міркування (критично важливо):**
- Міркуй КОРОТКО. Максимум 4–6 речень перед дією.
- Якщо текст міркування перевищує 800–1000 символів без tool call — це зациклення, зупинись.
- Не повторювати думки більше 3 разів поспіль.
- 3+ однакові tool call'и — зупинити цикл і змінити підхід.

### ✅ Перевірка готовності до синхронізації

Всі критичні файли перевірені та знайдені:
- ✅ `agents/Comfy-smart-lady.md` (103 рядки) — повний
- ✅ 6 SKILL.md файлів у `.github/skills/*/` — повні
- ✅ `.github/hooks/anti_loop.py` (317 рядків) — повний, з автоматичним логуванням циклів
- ✅ `.opencode/plugin/anti-loop.js` — є
- ✅ `manifest.json` — повна конфігурація синхронізації
- ✅ `VERSION` — "1.0.0"
- ✅ `scripts/sync-agent.py`, `install.sh`, `migrate-to-central-agent.py` — є

**Статус:** Готовий до повної синхронізації згідно плану в `docs/agent-sync-plan.md`.

---

## Версія 0.9.x (2026-08-14) — Початкова структура

### Основні файли
- `.github/agents/Comfy-smart-lady.md` — 103 рядки, повний файл інструкцій агента
- `.opencode/plugin/anti-loop.js` — JS плагін для детектування циклів
- `.clinerules/hooks/Loops.json` — конфігурація хуків
- `scripts/anti_loop.py` — Python скрипт анти-циклу (279 рядків)

### Навички агента
- `.github/skills/context-management/SKILL.md` — анти-цикл + очищення контексту
- `.github/skills/errors/SKILL.md` — перевірка помилок транскрипту
- `.github/skills/localization-qa/SKILL.md` — QA локалізації
- `.github/skills/safe-edit/SKILL.md` — безпечне редагування файлів
- `.github/skills/session-history/SKILL.md` — історія сесій
- `.github/skills/small-steps/SKILL.md` — адаптивна розбивка задач

### Додаткові інструменти
- `scripts/check-ai-co-authors.sh` — скрипт перевірки AI commit'ів
- `.github/knowledge-base/README.md` — структура бази знань
- `memories/session/`, `memories/repo/action-log_YYYY-MM-DD.md`, `memories/errors/error-log_YYYY-MM-DD.md` — журнали сесій та помилок

**Принцип роботи:** "Шукати реально працюючі механізми роботи коду, шукати варіанти розв'язання в інтернеті, тестувати код запускаючи сервер та аналізуючи код в робочому середовищі. Фіксувати всі події у відповідні журнали. Зберігати базу знань знайденого коду в інтернеті"

---