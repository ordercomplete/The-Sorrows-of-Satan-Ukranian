# План виправлень і тестувань перед публікацією

**Проєкт:** Comfy-smart-lady-agent
**Версія:** 1.0.0
**Дата створення:** 2026-08-22
**Статус:** підготовка до виправлень

## Інструкція для локальної моделі

Виконуй цей план послідовно, по одному пункту за раз. Перед кожним редагуванням:

1. Прочитай поточний файл повністю або достатній локальний фрагмент.
2. Назви одну перевірювану гіпотезу про причину проблеми.
3. Зроби найменшу можливу зміну.
4. Одразу запусти тест саме для зміненого файлу.
5. Не переходь далі, якщо тест не пройшов.

### Правила безпечної роботи

- Не видаляй існуючі журнали та не перезаписуй історію, тільки доповнюй коментарями про поточні зміни.
- Не копіюй `node_modules`, `__pycache__`, `*.pyc`, runtime state і секрети.
- Не запускай `--apply` у робочий проєкт без резервної копії або dry-run; для smoke-тесту використовуй тимчасову папку.
- Після кожного виправлення додай короткий запис у `AGENT/memories_agent/actions/action-log_YYYY-MM-DD.md`.
- Усі команди запускай із кореня `Comfy-smart-lady-agent`.
- Якщо команда завершується помилкою, збережи повний текст помилки, виправ лише її причину й повтори ту саму команду.

### Порядок виконання залишкових пунктів

#### Крок A — `.gitignore`

Мета: зробити правила публікації робочими.

Перевір:

```powershell
Get-Content -Raw -Encoding UTF8 .gitignore
```

Файл має містити правила, а не Markdown-шаблон. Мінімальний набір:

```gitignore
.opencode/node_modules/
**/node_modules/
__pycache__/
**/__pycache__/
*.pyc
*.pyo
.venv/
venv/
backup/
*.bak
*.tmp
```

Не додавай `memories/` до ignore автоматично: спочатку виріши, чи ці журнали мають бути частиною репозиторію. Після зміни перевір:

```powershell
git check-ignore -v .opencode/node_modules/example.js
git check-ignore -v AGENT/hooks/__pycache__/example.pyc
```

Очікуваний результат: обидва шляхи ігноруються.

#### Крок B — очищення службових файлів

Мета: не публікувати залежності, кеші та локальні артефакти.

Перевір список перед видаленням:

```powershell
Get-ChildItem -Recurse -File .opencode/node_modules | Measure-Object
Get-ChildItem -Recurse -File -Include *.pyc | Select-Object FullName
Get-Item .continue/.continue.rar -ErrorAction SilentlyContinue
```

Дозволено видаляти тільки те, що вже покривається `.gitignore` або не є вихідним матеріалом проєкту. Після очищення перевір, що Python і каталог усе ще працюють.

#### Крок C — шляхи OpenCode

Мета: перевірити роботу на Windows і не зламати Linux-сумісність.

Перевір значення `skills.paths` у `opencode.json`. Шлях `/AGENT/agents` може означати корінь диска, а не папку репозиторію. Порівняй із фактичним розташуванням і документацією OpenCode.

Перевір окремо:

```powershell
Get-Content -Raw -Encoding UTF8 opencode.json | ConvertFrom-Json
Test-Path AGENT/agents
Test-Path AGENT/skills
```

Не змінюй шлях лише через припущення: спочатку виконай smoke-тест OpenCode або перевір його документацію. Для `$schema` локальний файл уже існує: `AGENT/chats/opencode/config-schema.json`.

#### Крок D — документація

Мета: прибрати твердження, які суперечать фактичній структурі.

Порівняй документацію з командами:

```powershell
Get-ChildItem -Recurse -File AGENT,scripts,docs,templates | Select-Object FullName,Length
python -m py_compile AGENT/scripts/anti_loop.py AGENT/scripts/watch_agent_file.py scripts/sync-agent.py scripts/migrate-to-central-agent.py AGENT/scripts/generate-agent-catalog.py
```

Оновлюй лише підтверджені факти: шляхи, кількість файлів, назви canonical/source і статуси функцій. Не переписуй історичні записи в `memories/`.

#### Крок E — фінальні перевірки

Виконуй у такому порядку:

```powershell
# 1. Python
$files = Get-ChildItem -Recurse -File -Filter *.py | Where-Object { $_.FullName -notmatch '\\(__pycache__|node_modules)\\' }
foreach ($file in $files) { python -m py_compile $file.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }

# 2. JSON
$files = Get-ChildItem -Recurse -File -Filter *.json | Where-Object { $_.FullName -notmatch '\\(__pycache__|node_modules)\\' }
foreach ($file in $files) { Get-Content -Raw -Encoding UTF8 $file.FullName | ConvertFrom-Json | Out-Null }

# 3. JavaScript
node --check .opencode/plugins/anti-loop.js

# 4. Sync
python scripts/sync-agent.py --source . --target . --dry-run

# 5. Каталог
python AGENT/scripts/generate-agent-catalog.py
```

Після кожної секції перевіряй код завершення. Будь-який ненульовий код означає: зупинись, запиши помилку та виправ її до переходу далі.

#### Крок F — Git-підготовка

Мета: створити чистий перший коміт.

```powershell
git init
git status --short
git add --dry-run .
git diff --cached --check
```

Перед `git add .` перевір, що в списку немає `node_modules`, `__pycache__`, `*.pyc`, приватних ключів і небажаних runtime-логів. Перший коміт і `push` виконуй лише після ручного перегляду staged-списку.

### Формат звіту локальної моделі

Після кожного кроку записуй:

```text
Крок: [назва]
Зміна: [який файл і що змінено]
Тест: [точна команда]
Результат: PASS або FAIL
Наступна дія: [наступний пункт або причина зупинки]
```

## Мета

Підготувати репозиторій до безпечного заливання на GitHub: відновити виконувані файли, прибрати службові артефакти, узгодити канонічну структуру та пройти повторюваний набір тестів.

## 1. Критичні виправлення

- [x] Відновити справжній Python-код у `AGENT/scripts/anti_loop.py`. Перевірено: `py_compile`, порожній ввід, одиничний виклик, `SAME TARGET`, state та error-log.
- [x] Прибрати службовий хвіст `</content>` з `AGENT/scripts/watch_agent_file.py`. Перевірено: `py_compile` та безпечний імпорт модуля.
- [x] Запустити `python -m py_compile` для всіх Python-файлів. Перевірено 7 файлів поза `__pycache__` і `node_modules`, помилок немає.
- [x] Визначити єдине канонічне розташування `sync-agent.py` і `migrate-to-central-agent.py`. Вирішено залишити repository tooling у кореневому `scripts/`.
- [x] Перемістити або синхронізувати робочі скрипти до `AGENT/scripts/`, якщо `AGENT/` залишається джерелом істини. Не застосовується: `AGENT/` є канонічним для файлів агента, а кореневий `scripts/` — для інструментів репозиторію.
- [x] Відновити правильний вміст `.gitignore`. Перевірено: містить робочі правила для node_modules, __pycache__, *.pyc, .venv, backup.
- [x] Відокремити stub-шаблон від backup-файлів watcher-а: створено `AGENT/templates/stub_agents.md`.

## 2. Очищення репозиторію

- [x] Не включати `.opencode/node_modules/` до публічного репозиторію. Перевірено: node_modules відсутні.
- [x] Не включати `__pycache__/` і файли `*.pyc`. Перевірено: pyc-файлів немає, .gitignore покриває.
- [x] Перевірити, чи потрібен архів `.continue/.continue.rar`. Рішення: архів відсутній.
- [x] Перевірити відсутність токенів, API-ключів, паролів і приватних ключів. Перевірено: 0 результатів.
- [x] Вирішити, які runtime-логи `memories/` публічні, а які мають ігноруватися. Рішення: `memories/session/*.md`, `memories/repo/action-log_*.md`, `memories/errors/error-log_*.md` — у .gitignore.

## 3. Узгодження конфігурації

- [x] Перевірити шляхи `skills.paths` у `opencode.json` на Windows і Linux. Виправлено: `/AGENT/agents` → `./AGENT/agents`, `/AGENT/skills` → `./AGENT/skills`.
- [x] Переконатися, що `$schema` або доступний зовнішній URL, або підключена локальна `AGENT/chats/opencode/config-schema.json`. Залишено зовнішній URL, локальна копія є для довідки.
- [x] Відновити `manifest.json`: прибрати UTF-8 BOM і повернути очікуваний об’єкт із `files` та `stub_files`, потім звірити його з фактичною структурою `AGENT/`, `.github/`, `.opencode/`, `.clinerules/` і `.continue/`. Перевірено: 9 file rules, 2 stub rules і успішний sync dry-run.
- [x] Перевірити, що stub-файли посилаються на актуальний канонічний файл агента. Реальний `--apply` у тимчасовій папці створив stub із `${workspace}/AGENT/agents/Comfy-smart-lady.md`.
- [x] Замінити застарілі твердження в `README.md` — оновлено структуру репозиторію, кількість рядків і шляхи.

## 4. Функціональні тести

### Python

```powershell
$files = Get-ChildItem -Recurse -File -Filter *.py |
  Where-Object { $_.FullName -notmatch '\\(__pycache__|node_modules)\\' }
foreach ($file in $files) { python -m py_compile $file.FullName }
```

### JSON

```powershell
$files = Get-ChildItem -Recurse -File -Filter *.json |
  Where-Object { $_.FullName -notmatch '\\(__pycache__|node_modules)\\' }
foreach ($file in $files) {
  Get-Content -Raw -Encoding UTF8 $file.FullName | ConvertFrom-Json | Out-Null
}
```

### JavaScript

```powershell
node --check .opencode/plugins/anti-loop.js
```

### Синхронізація

```powershell
python scripts/sync-agent.py --help
python scripts/migrate-to-central-agent.py --help
python scripts/sync-agent.py --source . --target . --dry-run
```

Dry-run не повинен завершуватися помилкою і не повинен змінювати файли.

### Каталог

```powershell
python AGENT/scripts/generate-agent-catalog.py
```

Перевірити:

- HTML створено без помилок.
- У каталозі є `AGENT/`, `memories/`, `docs/`, `templates/` і кореневі Markdown-файли.
- Кнопка пересканування працює.
- Повторний запуск не створює дублікати.

### Безпека вмісту

```powershell
$patterns = 'api[_-]?key|secret|token|password|BEGIN [A-Z ]+ PRIVATE KEY|ghp_|github_pat_'
Select-String -Path (Get-ChildItem -Recurse -File).FullName -Pattern $patterns -CaseSensitive:$false
```

Команда не повинна знаходити реальні секрети.

## 5. Git-підготовка

- [x] Створити Git-репозиторій командою `git init`.
- [x] Перевірити `git status --short`.
- [x] Переконатися, що `node_modules`, кеші, runtime-стан і секрети не потрапляють у список. Виключено `AGENT/state/`, `.github/state/`, `.opencode/state/` через `.gitignore`.
- [x] Перевірити розмір майбутнього коміту. ~1 МБ, 98 файлів.
- [x] Переглянути `git diff --check`. Виправлено CRLF → LF у 94 текстових файлах (trailing whitespace).
- [x] Створити перший коміт лише після проходження всіх тестів. Коміт `eb4b56d`.
- [ ] Додати remote GitHub і виконати push після перевірки URL та гілки.

## Критерії готовності

Репозиторій можна публікувати лише коли:

- усі Python-файли компілюються без помилок;
- JSON і JavaScript проходять перевірку;
- sync dry-run працює з поточного кореня;
- каталог генерується та охоплює потрібні джерела;
- службові залежності й кеші виключені;
- документація відповідає фактичній структурі;
- Git-статус містить лише очікувані файли;
- перевірка секретів не знаходить реальних ключів.

## Підсумковий статус

**Готовність на момент створення плану:** не готовий до публікації.
**Основні блокери:** пошкоджені hook-файли, неправильний `.gitignore`, розсинхронізація `AGENT/scripts/` і `scripts/`, відсутність `.git` та зайві `node_modules`.
