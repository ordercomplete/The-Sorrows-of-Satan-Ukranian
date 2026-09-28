# Manifest.json Нотатки

## Категорії файлів

### Виконувані файли (copy_full)

- `AGENT/scripts/anti_loop.py` — Механізм запобігання циклам, відстежує запити агента та блокує нескінченні цикли за допомогою хешування signature(tool_name, tool_input) вхідних даних, закодованих у JSON; target() витягує filePath/path/target/uri з параметрів інструменту
- `AGENT/scripts/watch_agent_file.py` — Відстежує AGENT/agents/Comfy-smart-lady.md кожні 60 секунд за допомогою порівняння хешів MD5; створює резервні копії з часовими мітками в agent_config/backup-agent/ у форматі AGENT_YYYY-MM-DD_HH-MM-SS.zip; записує всі події в agent_config/watcher_log.txt
- `AGENT/scripts/agent_startup.py` — Скрипт оркестрації автозавантаження; перевіряє синтаксис anti_loop.py, watch_agent_file.py, str.translate.py через compile() перед запуском спостерігача як окремого процесу (CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS у Windows)
- `AGENT/scripts/str.translate.py` — Перекладач розкладки клавіатури EN↔UK за допомогою str.maketrans() з попередньо обчисленими таблицями перекладу; decode_text(text, to_ukrainian=True) конвертує текст з помилками між макетами
- `AGENT/scripts/vercel_error_tracker.py` — Відстеження та логування помилок Vercel AI Gateway

### Хуки-конфігурації (copy_full)

- `AGENT/hooks/Loops.json` — Конфігурація хука PreToolUse; викликає `python AGENT/scripts/anti_loop.py` з таймаутом 8с
- `AGENT/hooks/watch_agent_file.json` — Конфігурація хука PreToolUse; викликає `python AGENT/scripts/watch_agent_file.py` з таймаутом 8с
- `AGENT/hooks/str.translate.json` — Конфігурація хука для перекладу розкладки
- `AGENT/hooks/vercel_error_tracker.json` — Конфігурація хука для відстеження помилок Vercel

### Плагіни (copy_full)

- `AGENT/plugin/anti-loop.js` — JavaScript-реалізація анти-циклів для браузерних агентів
- `AGENT/plugin/startup.js` — JavaScript-плагін запуску

### Файли-заглушки (stub)

- `agents/Comfy-smart-lady.md` → `.github/copilot-instructions.md`, `.opencode/agents/Comfy-smart-lady.md`, `.clinerules/agents/Comfy-smart-lady.md`, `.continue/agents/Comfy-smart-lady.md` (заглушка, що посилається на канонічний AGENT/)
- `.clinerules/agent-startup.md` — топ-левел заглушка для Cline: файли безпосередньо в корені `.clinerules/` — єдиний рівень, який Cline завантажує в контекст як правила (підпапки не читаються). Без нього INIT-GATE не спрацьовує в Cline (v1.4.5)
- Усі файли `skills/*/SKILL.md` → заглушки, що посилаються на канонічний ${workspace}/AGENT/skills/*
  - context-management/SKILL.md
  - errors/SKILL.md
  - localization-qa/SKILL.md
  - safe-edit/SKILL.md
  - session-history/SKILL.md
  - small-steps/SKILL.md
- `knowledge-base/README.md` → посилання на ${workspace}/AGENT/knowledge-base/README.md

### Кореневі файли (copy_full)

Конфігурація, документація та скрипти, розповсюджені по цільових розташуваннях:

- `opencode.json`, `.continue/*`, `agent_config/*` — повні оригінали, що зберігають дозволи на виконання та структуру

## Ключові рішення щодо проектування

1. **Архітектура хуків**: `AGENT/hooks/` містить лише JSON-конфігурації, які викликають скрипти з `AGENT/scripts/`. Фактична обробка відбувається в `AGENT/scripts/*.py`
2. **Механізм запобігання циклу**: Використовує signature(tool_name, tool_input) для хешування вхідних даних, закодованих у JSON; target() витягує filePath/path/target/uri з параметрів інструменту; load_state()/save_state() керує AGENT/state/vscode_agent_anti_loop_state.json — усі працюють з метаданими/підписами, а не з повним вмістом файлу
3. **Життєвий цикл Watcher**: Відстежує зміни AGENT/agents/Comfy-smart-lady.md кожні 60 секунд за допомогою хеш-порівняння MD5, створює резервні копії з мітками часу в agent_config/backup-agent/ у форматі AGENT_YYYY-MM-DD_HH-MM-SS.zip, записує всі події в agent_config/watcher_log.txt
4. **Оркестрація запуску агента**: Перевіряє синтаксис anti_loop.py, watch_agent_file.py, str.translate.py через compile() перед запуском watcher як відокремленого процесу (CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS у Windows; start_new_session=True у Linux/macOS)
5. **Стратегія Stub проти Full**: ~15 повних копій зменшено до ~5 (~65% обсягу скорочення); Файли SKILL та база знань використовують механізм заглушок із шаблоном templates/stub_agents.md, який замінює заповнювач ${source_ref}

### Файли agent_config у root_files (copy_full)

- `agent_config/**` — усі робочі файли конфігурації, скрипти (`scripts/`), шаблони (`templates/`) та **усі бекап-теки**: `backup-agent/` (zip-бекапи AGENT від watcher) та `backup-chat/` (знімки стану чатів). За рішенням користувача (v1.4.2) обмеження на бекапи знято: `SKIP_DIRS` у `update-manifest.py` містить лише `{"__pycache__", "trash"}`, тож усі бекап-файли відображаються у структурі Агента та розповсюджуються sync-agent'ом.

## Історія версій

- v1.4.9 (2026-09-28): **Стандартизація форматування Markdown.** Правила `markdown-style-guide.md` та конфіг `.markdownlint.json` зафіксовано як обов'язкові для створення та редагування будь-яких `.md` файлів (включно з журналами `memories_agent/`, `session_*.md`, `action-log_*.md` тощо): додано підрозділ у `AGENT/agents/Comfy-smart-lady.md`, правило 5 у `AGENT/skills/safe-edit/SKILL.md`, оновлено інструкції в `AGENT/skills/session-history/SKILL.md` та `AGENT/knowledge-base/standards/markdown-style-guide.md`. Усі виявлені помилки markdownlint у файлах поточної доби виправлено (0 помилок).
- v1.4.8 (2026-09-28): **Markdownlint.** Додано `.markdownlint.json` (вимкнені MD013 — довгі рядки інструкцій, MD033/MD041 — HTML-коментарі INIT-GATE на початку стабів, MD034/MD036/MD040; MD009 br_spaces=2 для жорстких переносів, MD012 max=1, MD024 siblings_only) і `.markdownlintignore` (журнали `memories_agent`, корзини, бекапи, node_modules) — обидва в `EXTRA_ROOT_FILES` і розповсюджуються на хости. Форматовано ядро: канон (закрито незакритий код-блок шаблону часу, таблиця бекапів → стиль `| --- |`), `session-history/SKILL.md` (порожній рядок після таблиці), `errors/SKILL.md` (`#`-коментарі → абзаци/списки), `knowledge-base/README.md`, 8× SKILL. У `sync-agent.py` обидва генератори стабів додають перенос у кінці (MD047), 19 стабів перегенеровано. Результат: ядро 0 / стаби 0 помилок; лишок 734 — Фаза 2 (легасі-доки)
- v1.4.7 (2026-09-28): Ліміт зберігання бекапів знижено 10 → **3** за рішенням користувача: `AGENT/scripts/watch_agent_file.py` (`MAX_AGENT_BACKUPS`, `MAX_CHAT_BACKUPS`), `agent_config/scripts/cleanup_backup_agent.py` (`MAX_BACKUPS`), `agent_config/scripts/sync-agent.py` (`BackupManager.MAX_BACKUPS`); синхронізовано дублікат `AGENT/hooks/watch_agent_file.py` (він відставав від канону і не мав ротації chat-бекапів); оновлено таблиці бекапів у `AGENT/agents/Comfy-smart-lady.md` і `.opencode/plugins/STARTUP.md`; наявні 10+10 знімків підрізано до 3+3 через `delete_to_trash.py` (Корзина); доданий автостарт демона `.vscode/tasks.json` (`runOn: folderOpen` → `agent_startup.py`); гігієна sync — `_ignore_agent_runtime` і генерація `agent-lock.json` тепер виключають `state/`, `session/`, `trash/`, `__pycache__/`, `*.log`, `*.pyc` (lock 562 → 147 записів; до фіксу trash поїхав би на хости); **окремо (правка користувача, 2026-09-28):** `agent_config/.gitignore` переведено на робочі патерни `backup-agent/` і `backup-chat/` — бекапи більше не трекаються в git; у `manifest.json` бекапи лишаються в `root_files` (рішення v1.4.2), тому в клоні репозиторію цих файлів немає — рішення про виключення зі структури відкрите
- v1.4.6 (стан 2026-09-28, центр): після fast-forward до `8398707` перегенеровано `manifest.json` на центрі — 10 посилань на `backup-agent/AGENT_2026-09-02_*.zip` замінено фактичними 09-09 (ротація 09-02→09-09 у центрі пройшла без оновлення маніфесту); `agent-lock.json` перезібрано до v1.4.6 (173 файли), 19 стаб-файлів перегенеровано з PRIORITY-гейтом, створено знімок `backup-chat/backup_2026-09-28_10-15-52`
- v1.4.6: Усунено поведінковий обхід INIT-GATE: у чаті з доставленим правилом модель відповіла на «Привіт» без читання канонічного файлу (правило «simple question → answer directly» перебило гейт; механічного блокера в Cline немає). Виправлення: у канонічній інструкції додано блок «ПРІОРИТЕТ ГЕЙТУ» (гейт перемагає будь-який конфлікт інструкцій; перше повідомлення ЛЮБОГО типу починається з read_files); у шаблоні stub-ів фразу «Після привітання прочитайте» замінено на «Перед БУДЬ-ЯКОЮ відповіддю (включно з привітанням)» + HTML-коментар PRIORITY; inline-шаблон у `sync-agent.py` (секція files, action=stub) синхронізовано з тим же формулюванням; 6 checked-in stub-ів STUB_TARGETS у центрі перегенеровано з оновленого шаблону (раніше в центрі лежали старі копії без hard-gate); VERSION → 1.4.6
- v1.4.5: Виправлено непрацюючий INIT-GATE у Cline. Причина: (1) Cline завантажує в контекст лише .md/.txt безпосередньо в корені `.clinerules/` — stub-и в підпапках туди не потрапляли; (2) `.clinerules/hooks/Loops.json` Cline не виконує (це формат OpenCode/Continue), тож anti_loop-гейт не працював; (3) жорсткі INIT-GATE коментарі, додані на хості 2026-09-04 (backup 15-07-27), затерлися при оновленні, бо в центрі їх не було. Виправлення: `.clinerules/agent-startup.md` додано до STUB_TARGETS у `update-manifest.py` (тепер встановлюється на кожен хост), у шаблон `templates/stub_agents.md` додано жорсткі INIT-GATE HTML-коментарі; VERSION → 1.4.5
- v1.4.3: Виправлено `watcher_is_running()` у `AGENT/scripts/watch_agent_file.py` — фільтр процесів звіряє шлях поточного workspace (раніше ловив watcher іншого проєкту й казав "already running", через що локальний демон не стартував і бекапи накопичувались понад ліміт 10); watcher перезапущено detached
- v1.4.2: Знято обмеження на бекап-теки (SKIP_DIRS = {"__pycache__", "trash"}): `backup/`, `backup-chat/` та `backup-agent/` тепер повністю входять до `root_files` manifest.json (563 записи)
- v1.4.1: `agent_config/backup-agent/*.zip` додано до `root_files` manifest.json (прибрано "backup-agent" зі SKIP_DIRS у `update-manifest.py`); VERSION підвищено до 1.4.1
- v1.4.0: Оновлено manifest.json через update-manifest.py; синхронізовано структуру файлів; виправлено шляхи в manifest-notes.md (hooks → scripts)
- v1.2.0: Файли SKILL та база знань перетворені на заглушки; додано str.translate.py до оркестрації автозавантаження