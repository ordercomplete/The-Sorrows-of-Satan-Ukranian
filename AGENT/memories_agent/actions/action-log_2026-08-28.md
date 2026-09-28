# Журнал дій агента — 2026-08-28

## Запит користувача
«Перевір узгодженість додатку, особливо у питанні автозавантаження скриптів, також стосовно обов'язковості копіювання інструкцій з канонічної AGENT до .github. Думаю, що .github може прочитати інструкції за посиланням в AGENT\agents\Comfy-smart-lady.md.»

## Аудит узгодженості (13:20–13:45)

### Перевірено
1. ✅ Структура `.github/` vs `AGENT/` — hash-порівняння:
   - anti_loop.py, watch_agent_file.py, agent_startup.py, skills (6 шт), knowledge-base — SAME.
   - `str.translate.py` — був лише в `AGENT/hooks/`, у оболонках чатів НЕ розповсюджений.
2. ✅ Stub-файли агентів усіх 4 чатів — посилання на `${workspace}/AGENT/agents/Comfy-smart-lady.md`.
3. ✅ `.opencode/plugin/anti-loop.js` == `AGENT/plugin/anti-loop.js` (SAME).
4. ✅ `Loops.json` == у .github / .clinerules / .continue (SAME).
5. ❌ **`.github/copilot-instructions.md`** — містив жорсткий шлях `D:\GEN\...`, що ламає копії проекту на інших машинах.
6. ❌ **`agent_config/manifest.json`** — мав skills як `stub`, а генератор `update-manifest.py` виробляє `copy_full` у `.github/skills` та `.clinerules/skills` (фактичний стан файлів = copy_full). Тобто manifest був розсинхронізований з генератором.
7. ❌ **`sync-agent.py`** — падав при self-sync (`--source . --target .`): `WinError 32` при копіюванні файлу сам у себе; inline stub-шаблон вставляв абсолютний шлях; `UnicodeDecodeError` при читанні `git diff` на cp1251 Windows.
8. ❌ `update-manifest.py` не мав `hooks/str.translate.py` у DEFAULT_FILES → при перегенерації запис загубився б.

### Виконано
- ✅ `.github/copilot-instructions.md` переписано як настійливий stub: обов'язково прочитати канонічний файл `${workspace}/AGENT/agents/Comfy-smart-lady.md`. Жодних абсолютних шляхів.
- ✅ `agent_config/scripts/update-manifest.py`:
  - додано `hooks/str.translate.py` у DEFAULT_FILES (цілі: .github/hooks, .clinerules/hooks, .continue/hooks, .opencode/hooks);
  - `agents/Comfy-smart-lady.md` → завжди `stub` (розповсюдження інструкцій як посилань).
- ✅ `agent_config/scripts/sync-agent.py`:
  - self-sync guard (source == target → skip);
  - inline stub-шаблон використовує `${workspace}` замість абсолютного шляху;
  - `encoding='utf-8', errors='replace'` у всіх git subprocess;
  - inline stub-шаблон тепер настійливий («Після привітання читай та виконуй канонічний файл агента»).
- ✅ manifest.json перегенеровано (`update-manifest.py --apply`), виконано self-sync (`--apply`).
- ✅ `AGENT/scripts/str.translate.py` розповсюджено в `.github/hooks/`, `.clinerules/hooks/`, `.continue/hooks/`, `.opencode/hooks/` (SAME).
- ✅ Кореневі артефакти `skills/` та `knowledge-base/` (залишки старого manifest) видалено через `delete_to_trash.py`.
- ✅ README GitHub Copilot: «порожні папки» → «stub-посилання».

### 💡 Інсайти
- **Стратегія stub для .github працює**: GitHub Copilot автозавантажує `.github/copilot-instructions.md`, де записаний настійливий заклик прочитати канонічний файл. Повна копія інструкцій у `.github` НЕ потрібна.
- `manifest.json` треба підтримувати через «генератор → перегенерацію», а не руками, інакше він роз'їжджається з `update-manifest.py`.
- Self-sync (`--source <репо> --target <сам репо>`) — корисний прийом верифікації цілісності розповсюдження, тепер працює без помилок.

## Користувач уточнив принцип проєкту: жодних копій інструкцій у чатах (14:00–14:15)

Користувач зауважив, що я помилково змінила README GitHub Copilot на «копії канонічних» і взагалі перетворила skills на copy_full. Головна думка: **канонічні інструкції Агента (agents/, skills/, knowledge-base/) НЕ мають копій у папках чатів — лише посилання (stub) на файли в AGENT/**. Копією залишається тільки виконавчий код хуків/скриптів, який потрібен системі чату під час запуску.

### Виконано
- `update-manifest.py` build_files(): централізовано через `STUB_KEYS = {agents/*, skills/{d}/SKILL.md, knowledge-base/README.md}` → всі → `action=stub`; виконавчі скрипти лишаються `copy_full`. Виправлено хибний copy_full для skills попередньої під-дії.
- manifest.json перегенеровано (skills/6 + knowledge-base → stub).
- self-sync `--apply`: `.github/skills/*`, `.clinerules/skills/*`, `.github/knowledge-base/README.md`, `.clinerules/knowledge-base/README.md` → перетворено на stub-посилання `${workspace}/AGENT/...`. Старі повні копії BackupManager зберіг у `backup/`.
- Верифікація хешами: skills GH/CL ≠ AGENT (stub ✓); knowledge-base GH/CL ≠ AGENT (stub ✓); виконавчі копії (.github/hooks/anti_loop.py, str.translate.py, agent_startup.py, Loops.json, .opencode/plugin/anti-loop.js) = AGENT (SAME ✓).
- `agent_config/README.md`: структура .github/.clinerules перемальована — skills/knowledge-base як «stub-посилання», виконавчий код як «копія (виконавчий код)».
- README chats/github-copilot: повернуто правильне «stub-посилання на канонічні AGENT\skills та AGENT\knowledge-base».

## Післяобідні зміни агента (15:00-16:00)

### Щоденна синхронізація
- Виконано перший запуск доби: update-manifest.py --apply (14 files / 4 stubs / 29 root_files)
  + sync-agent.py --source . --target . --apply.
- str.translate.py розповсюджено в 4 оболонки; agent_config/.continue/ та manifest-notes.md
  вперше потрапили в manifest.
- test_install.ps1 пройшов успішно (чистий клон, усі перевірки True).

### Виведення migrate-to-central-agent.py з ужитку
- Видалено через delete_to_trash.py -> agent_config/trash/2026-08-28_migrate-to-central-agent.py.
- manifest.json перегенеровано (запис зник); README.md оновлено.

### Оновлення канонічної інструкції
- У AGENT/agents/Comfy-smart-lady.md додано підрозділ про оновлення структури
  (два тригери: подія - новий файл; доба - перший запуск). agent-catalog.html перегенеровано.

### Міграція агентних подій з memories/ у memories_agent/
- За запитом користувача: події, пов'язані зі змінами Агента, перенесено з
  memories/session/ та memories/repo/ у відповідні папки memories_agent/.
- Перенесено: сесія 2026-08-18 (автозавантаження агента) -> session/;
  інтеграція V3 2026-08-26 -> session/ + actions/.
- Дублі (08-14, 08-20, 08-28) в memories/ замінено крос-референсами,
  оскільки деталі вже є в actions/ відповідних дат.
- Деталі: cross-reference/external-links.md.


### [2026-08-28 20:54] FIX BUG-001: ManifestParser.parse() хибно стирає // у URL
- **Проблема:** regex re.sub(r'//.*?(?=\n|$)', '', content) стирає // у https:// URL-адресах у manifest.json,
  бо не розрізняє рядки JSON та коментарі. Це руйнує JSON -> Invalid control character at: line 6 column 28 (char 141).
  Блокує всю інсталяцію (install.ps1, sync-agent.py --dry-run/--apply/--update).
- **Виправлення:** замінено regex на контекстно-свідомий токенізатор _strip_jsonc_comments(),
  який видаляє // та /* */ лише поза межами JSON-рядків (з урахуванням екранування \").
  Видалено топ-рівневий import re (використовувався лише для багатого regex).
- **Файли:** agent_config/scripts/sync-agent.py (основний) + backup/.../sync-agent.py.
- **Тести:** створено test_manifest_parsing.py (6 unit-тестів, усі PASS). py_compile OK; --dry-run працює.
- **Manifest.json не редагувався** — він валідний.

### [20:59] 📝 Install_Comfy-smart-lady-agent.txt оновлено
- **Розділ 4** (УМОВИ СЕРЕДОВИЩА) розширено: додано конкретні команди встановлення та перевірки
  для Python, git, PowerShell, bash на Windows/Linux/macOS. Кожен інструмент має блоки
  «Встановити» та «Перевірити» + підсумкова перевірка.
- **Частина IV, Крок 2**: додано `agent_config/scripts/sync-agent.py` у py_compile‑список.

