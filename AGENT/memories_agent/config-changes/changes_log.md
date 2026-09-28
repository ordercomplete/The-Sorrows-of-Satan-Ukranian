# 📝 Зміни конфігурації

## Усунення дублікатів core scripts — 2026-08-31 20:10

### Проблема:
Я створила новий файл AGENT/scripts/startup_all.py замість використовувати вже існуючий .github/scripts/agent_startup.py.

### Рішення:
**AGENT/scripts/agent_startup.py вже робить все те саме:**
- ✅ Запускає watcher daemon через start_watcher() → запускає watch_agent_file.py як detached процес
- ✅ Валідізує core скрипти (anti_loop.py, watch_agent_file.py, str.translate.py)
- ✅ Перевіряє чи watcher уже запущений перед стартуванням
- ✅ Запускає синхронізацію через check_for_updates()

### Збережено:
**AGENT/scripts/startup_all.py залишається як єдина центральна точка завантаження для всіх чатів (.github/, .opencode/, .clinerules/).**  
**.github/scripts/agent_startup.py замінено посиланням на startup_all.py.

### Результат:
✅ Усунуто дублікати — один файл запускає watcher daemon, anti_loop.py, str.translate.py для всіх чатів.

---

## Структурне узгодження hook/скрипти — 2026-09-02 12:45

### Рішення користувача:
Папка хуків (`AGENT/hooks/`) має містити тільки **виконавчі файли**, а всі чати
мають посилатись і виконувати скрипти канонічно в **`AGENT/scripts/`**.

### Виконано:
- ✅ `AGENT/hooks/` — лишились тільки JSON-конфіги (`Loops.json`, `str.translate.json`,
  `vercel_error_tracker.json`, `watch_agent_file.json`); Python-скрипти перенесені в `AGENT/scripts/`.
- ✅ Всі виконавчі хуки чатів (`Loops.json` ×3, JS-завантажувачі opencode/clinerules/github/loader)
  викликають `AGENT/scripts/*.py`.
- ✅ `.py`-дублікати з `.github/hooks/`, `.clinerules/hooks/`, `.continue/hooks/`, `.opencode/hooks/`,
  `.github/scripts/agent_startup.py` — перенесені в Корзину (`AGENT/trash/`, delete_to_trash.py).
- ✅ `update-manifest.py` / `manifest.json`: розповсюдження `hooks/*.py` прибрано;
  `agent-lock.json` узгоджено (`sync-agent.py --update --apply`).
- ✅ Оновлено інсталятори та документацію (шляхи на `AGENT/scripts/`).

### Стан:
🟢 Узгоджено. Наступний крок — фінальна верифікація (py_compile, JSON, grep) та, за бажанням, commit.

---

## Міграція `.opencode/plugin/` → `.opencode/plugins/` (Варіант Б) — 2026-09-02 13:15

### Рішення:
Зробити `.opencode` за стандартом opencode: локальні плагіни автозавантажуються
з каталогу `.opencode/plugins/` (множина), без `plugin`-масиву в `opencode.json`.

### Виконано:
- ✅ `anti-loop.js`, `startup.js`, `STARTUP.md` перенесено в `.opencode/plugins/`;
  `.opencode/plugin/` (порожня) → Корзина.
- ✅ Канонічний `AGENT/plugin/startup.js` створено; `AGENT/plugin/anti-loop.js` уже актуальний.
- ✅ `opencode.json`: ключ `plugin` прибрано (плагіни тепер авто-вантажаться).
- ✅ `update-manifest.py` + `manifest.json`: `plugin/anti-loop.js` і `plugin/startup.js`
  → `.opencode/plugins/*.js`; `agent-lock.json` узгоджено.
- ✅ Документація та інсталятори оновлені на `.opencode/plugins/`.

### Стан:
🟢 Готово. Старт opencode тепер автоматично піднімає і watcher (startup.js), і anti-loop.

---

## Оновлення з upstream `ae2e4db` — 2026-09-02 18:50

### Проблема:
Агент відстає на 1 коміт від `origin/main`. Необхідно оновити з центрального репо.

### Дії:
- ✅ `git stash --include-untracked` — збереження локальних змін
- ✅ `git pull origin main` — fast-forward `e7bee21` → `ae2e4db`
- ✅ `git stash pop` — відновлення локальних змін
- ✅ `py_compile` усіх скриптів з нових шляхів → OK
- ✅ Видалено дублікат `AGENT/memories_аgent/` (кирилилиця) через `delete_to_trash.py`

### Що змінилося в upstream `ae2e4db`:
- **Restructuring**: перенесено Python-скрипти з `AGENT/hooks/` → `AGENT/scripts/`; `AGENT/hooks/` тепер містить лише JSON-конфіги
- **OpenCoder**: міграція `.opencode/plugin/` → `.opencode/plugins/`
- **Очищення**: видалено дублікати `.py`-файлів з оболонок чатів
- **Документація**: оновлено інсталятори, STARTUP.md, SCRIPTS_CATALOG.md
- **Бекапи**: додано файли бекапів у git

### Стан:
🟢 Оновлення завершене. Усі скрипти компілюються з нових шляхів. Конфігурація синхронізована.
## 2026-09-02 19:36 — Корекція ротації бекапів (ліміт 10)
- `AGENT/scripts/watch_agent_file.py`: prune тепер викликається у КОЖНОМУ циклі (не тільки після власного знімка) + на старті; сортування за ім'ям (таймстамп), а не mtime — sync скидає mtime при копіюванні між workspace.
- `agent_config/scripts/cleanup_backup_agent.py`: шлях від розташування скрипта (не від CWD), сортування за ім'ям.
- Причина багу: watcher (PID 35860) був запущений з D:/GEN/Comfy-smart-lady-agent і чистив чужу папку; sync-agent копіював знімки між workspace → 18/10.
- Перезапуск: старий daemon зупинено, watcher запущено з Music_Doc (PID 36532), бекапи 18→10 (8 шт у trash).

## 2026-09-02 20:30 — Механізм ротації 10 поширено на backup-chat
- `AGENT/scripts/watch_agent_file.py`: нова `prune_old_chat_backups()` (ліміт MAX_CHAT_BACKUPS=10), виклик на старті + щоциклу; сортування за ім'ям папки (mtime скидається sync-ом).
- `agent_config/scripts/sync-agent.py`: `_prune_old_backups` — сортування за ім'ям замість mtime.
- `agent_config/scripts/cleanup_backup_agent.py`: тепер ротує і папки backup-chat.
- 2 найстаріші папки (2026-08-29) → trash, 12→10. Скрипти синхронізовано в D:/GEN/Comfy-smart-lady-agent, watcher перезапущено (PID 3196).
## 2026-09-08 12:15 — Корекція `AGENT/agents/Comfy-smart-lady.md`: розмежування «проєктні записи vs записи про зміни Агента»
- **Причина:** проєктна сесія 2026-09-08 помилково створена в `AGENT/memories_agent/session/`
  (агентський журнал) вместо `memories_Under-word-app/session/`.
- **Виправлено в інструкціях:**
  - INIT-протокол п.2–3: тепер явно визначається тип сесії — ПРОЕКТНА
    (`memories_{назва-папки-проєкту}/session/`) vs ЗМІНИ АГЕНТА
    (`AGENT/memories_agent/session/`); п.5 уточнено: агентський файл — ЛИШЕ для змін
    структури Агента.
  - Розділ «Створення історії сесії»: прибрані неіснуючі шляхи `AGENT/memories/session/`
    і `AGENT/memories/actions/`; додано сводну таблицю «де робити записи (проєкт vs Агент)».
  - Розділ «Перед початком роботи»: `memories/` уточнено до `memories_{назва-папки-проєкту}/`.
- **Запис сесії 2026-09-08 перенесений:** `AGENT/memories_agent/session/...` → Корзина
  (delete_to_trash.py → `AGENT/trash/2026-09-08_session_2026-09-08.md`), поточне місто —
  `memories_Under-word-app/session/session_2026-09-08.md`.

## 2026-09-28 10:15 — Щоденна синхронізація + оновлення Агента з центру (v1.4.3 → v1.4.6)
- **Тригер:** перший запуск доби (INIT о 10:14); файлу сесії на 2026-09-28 не було
- **git fetch:** `origin/main = 8398707` («Comfy-smart-lady v1.4.6: sync from Under-word-app 2026-09-09»), локально було `d6bf1ff` (v1.4.3) → відставання 5 комітів
- **git merge --ff-only origin/main:** 42 файли, +1237/−6168. Склад: канон інструкцій (блок «ПРІОРИТЕТ ГЕЙТУ» + типи сесій), hard-gate `.clinerules/agent-startup.md`, 4 нові `AGENT/hooks/*.py`, 2 документи бази знань + `solutions/clinerules-init-gate-cline.md`, журнали 09-04/09-05/09-09, оновлені `sync-agent.py` та `update-manifest.py`, `VERSION` 1.4.6, ротація `backup-agent` (zip-и 09-09)
- **Виправлено стан `manifest.json`:** 10 посилань на zip-и 09-02, яких немає в HEAD (ротація без перегенерації) → `update-manifest.py --apply` → 36 root_files, відсутніх 0
- **sync-agent.py --source . --target . --apply:** `agent-lock.json` v1.4.2 → v1.4.6 (173 файли, installed_at 2026-09-28T10:15:52); перегенеровано 19 стаб-файлів з PRIORITY-гейтом; створено знімок `backup-chat/backup_2026-09-28_10-15-52`; ротація прибрала `backup_2026-08-29_14-17-18` (ліміт 10)
- **Стан після:** VERSION 1.4.6, manifest 1.4.6 (14 files / 6 stub / 36 root), lock 1.4.6, 4 хуки `.py` компілюються
- **Не зроблено:** запуск watcher (потрібне рішення), коміт/пуш (потрібне рішення)

## 2026-09-28 10:40 — v1.4.7: ліміт бекапів 10 → 3 + автостарт демона + гігієна sync
**Рішення користувача:** «повинно бути змінено до трьох»; автостарт — `.vscode/tasks.json`; наявні зайві бекапи — через Корзину (`delete_to_trash.py`)
- **Код:** `AGENT/scripts/watch_agent_file.py` — `MAX_AGENT_BACKUPS` і `MAX_CHAT_BACKUPS` 10 → 3; `agent_config/scripts/cleanup_backup_agent.py` — `MAX_BACKUPS` 10 → 3; `agent_config/scripts/sync-agent.py` — `BackupManager.MAX_BACKUPS` 10 → 3
- **Дублікат:** `AGENT/hooks/watch_agent_file.py` перезаписано канонічним скриптом (відставав від канону і не мав ротації chat-бекапів)
- **Документація:** таблиця бекапів і рядок про автостарт у `AGENT/agents/Comfy-smart-lady.md`; таблиця в `.opencode/plugins/STARTUP.md`; історія версій у `agent_config/manifest-notes.md`; `VERSION` 1.4.6 → **1.4.7**
- **Автостарт:** створено `.vscode/tasks.json` — задача з `"runOn": "folderOpen"` → `python AGENT/scripts/agent_startup.py` (піднімає детачений watcher при відкритті проєкту)
- **Підрізання стану:** 14 об'єктів (7 zip + 7 папок) → `AGENT/trash/` через `delete_to_trash.py`; залишилось **3 + 3**; лог `AGENT/trash/deletion_log.md`
- **Запуск демона:** watcher PID 23240 о 10:42:02 (initial scan 123 файли); знімок `AGENT_2026-09-28_10-42-16.zip`; ротація в лозі «ліміт 3»; реакція на подальші зміни — о 10:44:02 новий знімок + ротація
- **Гігієна sync:** `_ignore_agent_runtime` + генерація `agent-lock.json` тепер виключають `state/`, `session/`, `trash/`, `__pycache__/`, `*.log`, `*.pyc` → lock 562 → **147** записів
- **Стан:** VERSION 1.4.7 · manifest 1.4.7 (14 files / 6 stub / **29 root_files**, відсутніх 0) · lock 1.4.7 (147) · backup-agent 3 · backup-chat 3 · watcher живий
- **Не зроблено:** коміт/пуш (потрібне рішення користувача)

## 2026-09-28 11:47 — v1.4.8: markdownlint конфіг + форматування ядра (.md)
**Рішення користувача:** «Фаза 0+1: конфіг/ignore + ядро (канон, шаблони, скіли, стаби)»
- **Нові файли:** `.markdownlint.json` (вимкнені MD013/MD033/MD034/MD036/MD040/MD041; MD009 br_spaces=2; MD012 max=1; MD024 siblings_only) і `.markdownlintignore` (журнали, корзини, бекапи, node_modules) — додані в `EXTRA_ROOT_FILES` `update-manifest.py` → розповсюджуються на хости через manifest root_files
- **Форматування ядра** (тільки пробілли/переноси, текст не змінювався): автофікс `markdownlint-cli --fix` + ручні правки `AGENT/agents/Comfy-smart-lady.md` (закрито незакритий код-блок шаблону часу, розділювач таблиці → стиль `| --- |`), `AGENT/skills/session-history/SKILL.md` (порожній рядок після таблиці), `AGENT/skills/errors/SKILL.md` (`#`-коментарі з .py → абзаци/списки/`##`), `AGENT/knowledge-base/README.md`, 8× `AGENT/skills/*/SKILL.md`
- **Генератори стабів:** `sync-agent.py` — inline-шаблон і `StubGenerator.generate_stub` тепер гарантують перенос у кінці файлу (MD047); 19 стаб-файлів перегенеровано `sync-agent --apply`
- **Верифікація:** `npx markdownlint-cli --config .markdownlint.json` → ядро **0**, стаби **0**; ignore-файл перевірено (журнали не лінтяться); лишок по репо **734** = Фаза 2 (легасі-доки)
- **Стан:** `VERSION` **1.4.8**, manifest 1.4.8 (root_files 29 → 31 з конфігом лінтера), lock оновлено

## 2026-09-28 11:05 — Бекапи переведено в git-ignore (правка користувача) + підготовка коміту v1.4.7
**Запит користувача:** «Я змінив на backup-agent/ backup-chat/. Перевір та можна комітити»
- **Перевірка правки:** `agent_config/.gitignore` тепер містить `backup-agent/` і `backup-chat/`; `git check-ignore -v --no-index` підтверджує їхню дію (раніше `./backup-agent` і `./backup-chat` були мертвими — git не підтримує провідне `./`)
- **Наслідок:** нові знімки (3 zip + 3 папки, 181 файл) більше не потрапляють у git; раніше трековані бекапи вже видалені з диска ротацією, тому коміт фіксує їхні видалення (D, 1031 запис) — після коміту в git не залишається жодного бекап-файлу
- **Відкритий нюанс:** `manifest.json` v1.4.7 усе ще перелічує `backup-agent/*.zip` як `root_files` (рішення v1.4.2), тобто в клоні репозиторію цих файлів немає — sync з клону друкуватиме «Пропущено в локу (нема в джерелі)». Рішення про виключення бекапів зі структури — за користувачем
- **Коміт:** виконано v1.4.7 (ліміт 3 + автостарт watcher + гігієна sync + git-ignore бекапів). Пуш — окремим рішенням

## 2026-09-28 12:35 — v1.4.9: закріплення Markdown Style Guide для створення файлів .md

**Запит користувача:** «Пропиши у правилах створення будь-яких файлів .md використовувати правила форматування з AGENT\knowledge-base\standards\markdown-style-guide.md, бо у новостворенному AGENT\memories_agent\actions\action-log_2026-09-28.md купа стилістичних помилок.»

**Зміни:**

- **Канонічні інструкції (`AGENT/agents/Comfy-smart-lady.md`):** додано обов'язковий підрозділ «Стандарти створення та редагування файлів .md (Markdown)» із переліком ключових вимог: відокремлення заголовків MD022, списків MD032, код-блоків MD031, відсутність подвійних порожніх рядків MD012, перенос у кінці MD047, коректні таблиці MD060.
- **Навичка журналювання (`AGENT/skills/session-history/SKILL.md`):** додано обов'язкове правило суворого дотримання Markdown Style Guide для всіх типів журналів (`session_*.md`, `action-log_*.md`, `error-log_*.md`).
- **Навичка безпечного редагування (`AGENT/skills/safe-edit/SKILL.md`):** додано правило 5 про стандарти Markdown для будь-яких `.md` файлів.
- **Стандарт (`AGENT/knowledge-base/standards/markdown-style-guide.md`):** у принципах явно закріплено вимогу дотримання стандарту для журналів сесій і дій пам'яті Агента та проєктів.
- **Виправлення журналів поточної доби:** файли `action-log_2026-09-28.md` та `session_2026-09-28.md` повністю відформатовано, перевірено лінтером — **0 помилок**.
- **Синхронізація:** `VERSION` → **1.4.9**, оновлено `manifest.json` та системні стаби через `sync-agent.py --apply`.
