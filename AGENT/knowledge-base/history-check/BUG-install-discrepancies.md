# BUG: Розбіжності інсталяції Comfy-smart-lady-agent (документація vs фактична реалізація v1.4.0)

**Тип:** Розбіжності документації з кодом (documentation/implementation gap)
**Версія Агента:** 1.4.0 (перевірено на чек-ауті локального репо)
**Репо (джерело істини):** https://github.com/ordercomplete/Comfy-smart-lady-agent.git
**Локальний клон:** `D:\GEN\Comfy-smart-lady-agent`
**Документація:** `Install_Comfy-smart-lady-agent.txt` (Частини I–V)
**Цільовий проєкт (де виявлено):** `D:\GEN\Music processing and enhancement. Documentation`

---
**Статус: ✅ ЗАКРИТО — усі розбіжності виправлено у v1.4.0 (2026-08-30).**

- Р.1+Р.6: `sync-agent.py --apply` тепер копіює все ядро `AGENT/` (крім `state/`, `session/`, `*.log`); dry-run це показує.
- Р.2: створено `AGENT/.gitignore` у репо — запис manifest `.gitignore -> AGENT/.gitignore` більше не дає «Файл не знайдено».
- Р.3: локальні `.gitignore` (`.github/`, `.clinerules/`, `.continue/`, `agent_config/`) створено в репо та додано в `root_files` manifest — роздаються при `--apply`.
- Р.4: `trash/.gitignore` + `trash/deletion_log.md` додано (force-add), роздаються через `root_files`; `AGENT/trash/` приходить з ядром.
- Р.5: `agent-lock.json`/`status`/`remove`/`gitignore` реалізовані в v1.4.0; lock тепер включає і файли ядра `AGENT/`.
- Р.7: ядро `AGENT/` розгортає лише `sync-agent.py --apply`; дублювання Кроку 2 прибрано з `install.ps1`/`install.sh`.

---

## Короткий зміст (TL;DR)

Реінсталяція через **Спосіб B** (`sync-agent.py --source ... --target . --apply`) не відтворює стан,
який вимагає Частина IV: **не створюється ядро каталогу `AGENT/`**, не роздаються локальні
`.gitignore`, не створюється коренева проєктна корзина `trash/`. Частина `agent-lock.json +
status/remove/gitignore`, яку `BUG-agent-lock.md` називає нереалізованою, у **v1.4.0 насправді
реалізована** — цей баг-репорт застарів і потребує оновлення.

---

## Розбіжність 1 — Ядро `AGENT/` НЕ розгортається способом B (найкритичніша)

### Заявлено в документації
- `Install_Comfy-smart-lady-agent.txt`, Частина II, «СПОСІБ B — ручна інсталяція», Крок 4:
  > «Застосуй синхронізацію (**копіює AGENT/**, .github/, .clinerules/, .continue/, .opencode/,
  > agent_config/, opencode.json, локальні .gitignore): python sync-agent.py --source ... --apply»
- Частина I §1: «Уся конфігурація Агента живе в папці agent_config/ (… manifest.json …)», ідея — `AGENT/` = канонічне ядро.

### Факт (з кодом v1.4.0)
`agent_config/scripts/sync-agent.py` у режимі `--apply` **не копіює** дерево `AGENT/` у цільовий проєкт.
Причина — у `agent_config/manifest.json` немає жодного запису з `target_paths`, що вказує всередину `AGENT/`:

- `source_root = "AGENT"`, але всі `target_paths` записів `files` ведуть у `.github/` і `.clinerules/`.
- канон `"agents/Comfy-smart-lady.md"` має `{"action": "stub", "target_paths": [".github/copilot-instructions.md"]}` —
  тобто канон НЕ розгортається в `AGENT/agents/Comfy-smart-lady.md`, а лише генерується stub у `.github/`.
- Жодних записів для `AGENT/hooks`, `AGENT/skills`, `AGENT/knowledge-base`, `AGENT/scripts`,
  `AGENT/plugin`, `AGENT/templates`, `AGENT/chats`, `AGENT/memories_agent`, `AGENT/trash` у `files` НЕМАЄ.

Ядро `AGENT/` приносить **тільки** `install.ps1` (Спосіб A), рядок 46:
```powershell
Copy-Item -Recurse -Force (Join-Path $TmpDir "AGENT\*") "./AGENT/"
```
`install.sh` — аналогічно. Тобто Спосіб B сам по собі дає неповну встановлену систему.

### Відтворення
```
# У ЧИСТОМУ цільовому проєкті
python D:\GEN\Comfy-smart-lady-agent\agent_config\scripts\sync-agent.py --source D:\GEN\Comfy-smart-lady-agent --target . --apply
Test-Path AGENT/agents/Comfy-smart-lady.md   # False (!) — каталог AGENT/ взагалі не створюється
```
Підтверджено в цій дійсній реінсталяції 2026-08-30: після `--apply` каталог `AGENT/` у цільовому проєкті був відсутній
і його довелося копіювати з репо вручну.

### Вплив
- Відсутній канонічний інструкційний файл `AGENT/agents/Comfy-smart-lady.md`;
- відсутні реальні `AGENT/knowledge-base`, `AGENT/skills`, `AGENT/hooks` (лише стаб-копії в оболонці);
- відсутній плагін anti-loop тощо аж до повного ядра Агента;
- агент «працює» на стабах, посилання `\`${workspace}/AGENT/...\`` у стабах веде в неіснуючу папку.

### Рекомендоване виправлення
1. Або зробити Спосіб A (`install.ps1` / `install.sh`) єдиним штатним способом повної установки, а Спосіб B позначити як «лише оновлення конфіг-оболонки»;
2. Або розширити `sync-agent.py`/`manifest.json`: додати секцію (напр. `agent_core`) або правило, що копіює структуру `source_root="AGENT"` у цільовий `AGENT/` при `--apply`;
3. Або принаймні чесно описати в Частині II, що Спосіб B не розгортає `AGENT/`.

---
## Розбіжність 2 — manifest посилається на `AGENT/.gitignore`, якого НЕМАЄ в репо

### Заявлено
- `agent_config/manifest.json`, секція `files`:
  ```json
  ".gitignore": { "action": "copy_full", "target_paths": ["AGENT/.gitignore"] }
  ```
  (має бути: файл `.gitignore` у корені `AGENT/` репо копіюється в цільовий `AGENT/.gitignore`).

### Факт
У центральному репо **немає** файлу `AGENT/.gitignore`. Фактично в репо є лише:
- `D:\GEN\Comfy-smart-lady-agent\.gitignore` (кореневий)
- `D:\GEN\Comfy-smart-lady-agent\.opencode\.gitignore`

Перевірка:
```
Get-ChildItem -Recurse -Force -Filter '.gitignore' D:\GEN\Comfy-smart-lady-agent |
  Where-Object { $_.FullName -notmatch 'node_modules' }
# => лише кореневий + .opencode/.gitignore
```

### Симптом під час інсталяції
При `--apply` sync-agent друкує:
```
❌ Файл не знайдено: D:\...\Comfy-smart-lady-agent\AGENT\.gitignore
```
скрипт не падає (код іде далі), але `AGENT/.gitignore` у цільовий проєкт **не роздається**.

### Виправлення
Додати до центрального репо файл `AGENT/.gitignore` (серія правил із Частини I §2):
```
__pycache__/
*.pyc
state/
*.log
AGENT/trash/*
```

---

## Розбіжність 3 — Локальні `.gitignore` НЕ розповсюджуються автоматично

### Заявлено
`Install_Comfy-smart-lady-agent.txt`, Частина I §2:
> «кожна папка Агента несе власний локальний .gitignore … **Усі вони розповсюджуються автоматично через
> manifest.json**» — перелічені: `AGENT/.gitignore`, `.github/.gitignore`, `.clinerules/.gitignore`,
> `.continue/.gitignore`, `trash/.gitignore`.

### Факт
- У `manifest.json` є **тільки** запис `".gitignore" -> "AGENT/.gitignore"` (див. Розбіжність 2), і навіть він не знаходить джерело.
- **Немає жодних записів** для `".github/.gitignore"`, `".clinerules/.gitignore"`, `".continue/.gitignore"`, `"trash/.gitignore"`.
- У репо цих файлів теж немає.

### Відтворення
Після `--apply` у цільовому проєкті:
```
Test-Path AGENT/.gitignore       # False
Test-Path .github/.gitignore     # False
Test-Path .clinerules/.gitignore # False
Test-Path .continue/.gitignore   # False
Test-Path trash/.gitignore       # False
```
У цій реінсталяції всі шість `.gitignore` (включно з `agent_config/.gitignore`) довелося створювати вручну в цільовому проєкті.

### Вплив
Ігнор-правила `__pycache__/`, `*.pyc`, `state/`, `*.log` не діють у піддеревах `AGENT/`, `.github/`, `.clinerules/`, `.continue/` — сміття Python і стан можуть потрапляти в гіт хоста.

### Виправлення
Додати в репо `.github/.gitignore`, `.clinerules/.gitignore`, `.continue/.gitignore`, `trash/.gitignore`
(і за бажанням `agent_config/.gitignore`), та додати їх як окремі записи в `manifest.json` (`files`), щоб вони
копіювались у цільовий проєкт при `--apply`.

---

## Розбіжність 4 — Корзини не розгортаються (частково)

### Заявлено
- Частина I §3: «ДВІ КОРЗИНИ … AGENT/trash/ та trash/ (у корені)»;
- Частина IV Крок 4: «Корзини готові (обидві з логами): `AGENT/trash/deletion_log.md` і `trash/deletion_log.md`».

### Факт
- **Спосіб B** (`sync-agent.py`) не створює жодної корзини.
- **Спосіб A** (`install.ps1`) копіює `AGENT/*` з репо → якщо в репо є `AGENT/trash/deletion_log.md`, то з'явиться `AGENT/trash` (у нашому репо він є).
- **Кореневу проєктну `trash/` з логом не створює жоден спосіб** — у центральному репо немає кореневого `trash/`.
- `delete_to_trash.py` створить корзини «на льоту» при першому видаленні, але одразу після встановлення Частина IV Крок 4 не виконується.

### Відтворення
Після `--apply` (Спосіб B, чистий проєкт):
```
Test-Path AGENT/trash/deletion_log.md   # False
Test-Path trash/deletion_log.md         # False
```
Після `install.ps1` — коренева `trash/deletion_log.md` усе одно `False`.

### Виправлення
- У репо: додати `trash/.gitignore` (правило «ігнорує все, крім .gitignore і deletion_log.md`) і `trash/deletion_log.md`;
- Роздавати встановлення в обох способах (напр. у `manifest.json` `files` або в install-скриптах).

---

## Розбіжність 5 — Статус `agent-lock.json` / команд `status` / `remove` / `gitignore`

### Заявлено
- `Install_Comfy-smart-lady-agent.txt`, Частина I §2: lock створюється після `--apply`, є команди `status`, `remove`, `gitignore`.

### Факт у v1.4.0 (несподівано)
`agent-lock.json`, а також підкоманди `status`, `remove`, `gitignore` **РЕАЛІЗОВАНІ** в коді:
- клас `AgentLockManager` (рядки ~316–400) — читання/запис `agent-lock.json`;
- функції `cmd_status`, `cmd_remove`, `cmd_gitignore` (секція «New commands: status, remove, gitignore», рядки ~502+);
- генерація lock після `--apply` (вивід: «Lock saved …», «Agent lock file generated: agent-lock.json»);
- розгалуження підкоманд у `main()` (рядки ~946–956).

**Але є проблема відповідності:** `BUG-agent-lock.md` (v1.3.0) стверджує, що ці можливості НЕ реалізовані.
Цей баг-репорт **застарів** для v1.4.0 і вводить в оману.

### Виправлення
- Оновити/закрити `BUG-agent-lock.md`, вказавши, що на v1.4.0 `status`/`remove`/`gitignore` реалізовані;
- Переконатися, що `cmd_gitignore` реально дописує шляхи в локальні `.gitignore` (потребує юніт-перевірки);
- Якщо планується повністю покладатися на lock — дочекатися, щоб він включав і ядро `AGENT/` (див. Розбіжність 1), інакше `status` не покаже файли ядра.

---

## Розбіжність 6 — Dry-run не показує розгортання ядра AGENT/

### Заявлено (по суті)
`Install_Comfy-smart-lady-agent.txt`, Частина II, Спосіб B Крок 3: «Dry-run — ПОДИВИСЬ, що зміниться».

### Факт
`--dry-run` у Способі B перелічує лише записи `manifest.json` (стаби + конфіг), **не показуючи** жодного копіювання ядра `AGENT/`, бо його і не буде. Тобто dry-run створює хибне враження повної картини змін.

### Виправлення
Після вирішення Розбіжності 1 dry-run автоматично почне показувати ядро. Додатково — переконатися, що dry-run не редагує lock (`agent-lock.json` у dry-run НЕ створюється).

---

## Розбіжність 7 — Неузгодженість install.ps1 та sync-agent.py щодо застосування

### Факт
- `install.ps1` (Крок 4) запускає `sync-agent.py --apply`, але цей Спосіб A скопіював ядро `AGENT/`
  вже у Крок 2 (рядок 46), тобто ядро приходить з репо двома шляхами.
- `install.ps1` Крок 5 явно перевіряє `.opencode/plugin/anti-loop.js` і при відсутності друкує попередження «скопіюйте вручну», хоча `sync-agent.py --apply` за manifest повинен був вже його скопіювати. Це створює невизначеність щодо того, хто відповідає за які файли.

### Виправлення
Узгодити відповідальність: ядро `AGENT/` розгортає тільки install (Спосіб A), а конфіг-оболонки — sync-agent. Прибрати надлишкові попередження або перевірити фактичний стан.

---

## Підсумкова таблиця оцінки «заявлено vs факт»

| # | Пункт документації | Факт у v1.4.0 | Статус |
|---|--------------------|---------------|--------|
| 1 | Спосіб B копіює `AGENT/` | `AGENT/` не створюється | ❌ НЕ реалізовано |
| 2 | `AGENT/.gitignore` роздається | файлу немає в репо → «Файл не знайдено» | ❌ НЕ реалізовано |
| 3 | Локальні `.gitignore` роздаються автоматично | немає файлів та записів у manifest | ❌ НЕ реалізовано |
| 4 | Обидві корзини з логами після встановлення | `trash/` (коренева) не створюється | ⚠️ Частково |
| 5 | `agent-lock.json` + `status/remove/gitignore` | реалізовано в v1.4.0 | ✅ Реалізовано (але `BUG-agent-lock.md` застарів) |
| 6 | dry-run показує всі зміни | не показує ядро `AGENT/` | ❌ НЕ реалізовано |
| 7 | install.ps1 vs sync-agent узгоджені | дублювання, надлишкові перевірки | ⚠️ Неузгоджено |

---

## Команди для відтворення (на Windows PowerShell)

```powershell
# 1) Спосіб B установи в чистий проєкт
python D:\GEN\Comfy-smart-lady-agent\agent_config\scripts\sync-agent.py `
  --source D:\GEN\Comfy-smart-lady-agent --target . --apply

# 2) Перевірки Частини IV — що НЕ виконується
Test-Path AGENT/agents/Comfy-smart-lady.md   # False (ядро відсутнє)
Test-Path AGENT/.gitignore                   # False
Test-Path .github/.gitignore                 # False
Test-Path trash/deletion_log.md              # False

# 3) Перевірка стану lock (реалізовано в v1.4.0)
python agent_config\scripts\sync-agent.py status
```

---

## Рекомендована першочергова черга виправлень (для Агента)

1. **Розбіжність 1** — розгортання ядра `AGENT/` Спосібом B (найкритичніша, блокує повноцінну роботу).
2. **Розбіжності 2 і 3** — додати відсутні `.gitignore` у репо + записи в `manifest.json`.
3. **Розбіжність 4** — додати кореневу `trash/` з логом і `.gitignore`.
4. **Розбіжність 5** — оновити/закрити `BUG-agent-lock.md` (він описує v1.3.0 і вводить в оману).
5. **Розбіжності 6 і 7** — узгодити dry-run і логіку install vs sync.

---

Файл підготовлено Агентом 2026-08-30 за фактом реальної реінсталяції в
`D:\GEN\Music processing and enhancement. Documentation` (версія 1.4.0).