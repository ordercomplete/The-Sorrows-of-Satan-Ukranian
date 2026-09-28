========================================================================
COMFY-SMART-LADY AGENT — ВСІ СКРИПТИ (версія 1.4.0)
========================================================================
Дата створення: 29 серпня 2026

Цей файл описує всі існуючі скрипти Agent-а та їх функціонал.

========================================================================
ЧАСТИНА I — ГЛАВНІ СКРИПТИ В agent_config/scripts/
========================================================================

1. sync-agent.py
   Призначення: Основний скрипт синхронізації файлів Агента в проект.
   
   Команди:
     python agent_config/scripts/sync-agent.py --source <path> --target . [--dry-run | --apply]
     python agent_config/scripts/sync-agent.py status [--verbose]
     python agent_config/scripts/sync-agent.py remove [--force]
     python agent_config/scripts/sync-agent.py gitignore
   
   Аргументи:
     --source <path>      Шлях до центрального репо (за замовчуванням — поточна папка)
     --target .           Цільова директорія проекту
     --dry-run            Показати що зміниться без застосування
     --apply              Застосувати синхронізацію
     --update             Оновити існуючий проект
     --pull               Pull з центрального репо перед синхронізацією
     --check-update       Перевірити наявність нової версії Агента (без змін)
   
   Що робить:
     - Завантажує manifest.json
     - Копіює файли типу files, root_files, stub_files
     - Створює agent-lock.json після --apply
     - Підкоманди status / remove / gitignore працюють на основі agent-lock.json
     - remove видаляє ЛИШЕ Agent-файли (через Корзину: AGENT/* → AGENT/trash/, решта → trash/)
     - Кореневий .gitignore цільового проєкту НЕ змінюється (ігнор через локальні .gitignore папок)

2. update-manifest.py
   Призначення: Авто-генерація/оновлення manifest.json на основі структури AGENT/.
   
   Команди:
     python agent_config/scripts/update-manifest.py [--dry-run | --apply]
   
   Що робить:
     - Сканує директорії .github/, .clinerules/, .opencode/, .continue/
     - Створює секції files, stub_files, root_files
     - Додає локальні .gitignore для кожної папки Агента

3. delete_to_trash.py (повертається до agent_config/scripts/)
   Призначення: Корзина для видалених файлів — переміщує файл замість видаляти.
   
   Команди:
     python agent_config/scripts/delete_to_trash.py <шлях> [--reason "причина"] [--dry-run]
   
   Логіка:
     - Файли AGENT/* → AGENT/trash/ + лог у deletion_log.md
     - Файли проекту в корені → trash/ + лог
     - Маршрутизація автоматична за розташуванням файлу

4. install.ps1 (в кореневому каталозі, не в scripts/)
   Призначення: Повна установка на Windows через PowerShell.
   
   Команда:
     powershell -ExecutionPolicy Bypass -File agent_config\scripts\install.ps1 [URL_репозиторію]
   
   Що робить (внутрішні кроки):
     1. Клонувати центральне репо у temp
     2. Скопіювати ядро AGENT/
     3. Показати dry-run синхронізації
     4. Застосувати --apply
     5. Запустити перевірки (py_compile)
     6. Прибрати temp

5. install.sh (в кореневому каталозі, не в scripts/)
   Призначення: Повна установка на Linux/macOS/Git Bash через bash.
   
   Команда:
     bash agent_config/scripts/install.sh [URL_репозиторію]

6. test_install.ps1 (в кореневому каталозі)
   Призначення: Тестування інсталятора у тимчасовій папці.
   
   Команда:
     .\agent_config\scripts\test_install.ps1
   
   Перевіряє:
     - ✅ AGENT/agents/Comfy-smart-lady.md на місці
     - ✅ AGENT/scripts/anti_loop.py на місці
     - ✅ .clinerules/hooks/Loops.json на місці
     - ⚠️  .opencode/plugins/anti-loop.js відсутній (попередження)

========================================================================
ЧАСТИНА II — СКРИПТИ В AGENT/scripts/
========================================================================

7. agent_startup.py
   Призначення: Запуск сервісів Comfy-smart-lady при старті агента.
   
   Що робить:
     - Валідує критичні файли (anti_loop.py, watch_agent_file.py, str.translate.py)
     - Запускає watcher у фоні
     - Перевіряє оновлення (режим notify)

8. generate-agent-catalog.py
   Призначення: Генерація каталогу Агента на основі manifest.json.

========================================================================
ЧАСТИНА III — СКРИПТИ В AGENT/scripts/ (канонічне виконання)
========================================================================

9. anti_loop.py (канон, у AGENT/scripts/)
   Призначення: Логіка анти-циклу для аналізу tool call'ів перед виконанням.
   
   Використовується через: .opencode/plugins/anti-loop.js
   
10. watch_agent_file.py (канон, у AGENT/scripts/)
    Призначення: Моніторинг файлів Агента на зміни.

11. str.translate.py (канон, у AGENT/scripts/)
    Призначення: Переклад рядків інтерфейсу українською мовою.

   Виконавчі файли JSON у AGENT/hooks/: Loops.json, str.translate.json,
     vercel_error_tracker.json, watch_agent_file.json. Python-скрипти
     в оболонки чатів НЕ копіюються — всі чати викликають канонічні AGENT/scripts/.
     (в оболонках лишаються тільки виконавчі JS/JSON, див. Частину VI).
     
     

========================================================================
ЧАСТИНА IV — ПЛАГІН В .opencode/plugins/
========================================================================

12. anti-loop.js
    Призначення: Anti-hook перехоплення tool call'ів ДО виконання.
    
    Логіка:
      - Перехоплює виклики інструментів (tool.execute.before)
      - Передає дані у Python-скрипт anti_loop.py
      - Отримує рішення: allow, deny, або reset лупи

========================================================================
ЧАСТИНА V — STUB-ФАЙЛИ В .github/agents/, .clinerules/agents/ тощо
========================================================================

13. Comfy-smart-lady.md (4 копії)
    Розташування:
      - .github/agents/Comfy-smart-lady.md
      - .clinerules/agents/Comfy-smart-lady.md
      - .continue/agents/Comfy-smart-lady.md
      - .opencode/agents/Comfy-smart-lady.md
    
    Призначення: Короткі посилання на канонічні інструкції в AGENT/.
    
    Зміст (приблизно):
      # Comfy-smart-lady — посилання на канонічні інструкции
      
      Після привітання читай та виконуй канонічний файл агента:
      
      `${workspace}/AGENT/agents/Comfy-smart-lady.md`
      
      Цей файл є stub-посиланням. Всі зміни до інструкцій вносяться тільки 
      в канонічний файл у `AGENT/`.

========================================================================
ЧАСТИНА VI — ВИКОНАВЧІ ФАЙЛИ ХУКІВ У ОБОЛОНКАХ ЧАТІВ
========================================================================

14. Loops.json (виконавчий, копіюється в чати .github/.clinerules/.continue)
    Команда всередині: `python AGENT/scripts/anti_loop.py`
    
    

15. JS-завантажувачі (виконавчі, у чатах):
      - .opencode/plugins/anti-loop.js, startup.js

      - .clinerules/hooks/startup.js
      
    
    Python-скрипти в чати НЕ копіюються — див. ЧАСТИНА III.

16. (прибрано)
    (прибрано)
    
    (прибрано)

========================================================================
ДОДАТОК — ЧОМУ НАЗВИ РІЗНІ: hooks (хуки) vs plugins (плагіни)
========================================================================

Різні назви папок — це НЕ розсинхрон, а свідоме наслідування
конвенцій кожної платформи при єдиному канонічному ядрі:

  AGENT/scripts/*.py   ← єдине джерело виконання (для всіх чатів)
  AGENT/hooks/*.json   ← хук-конфіги для Cline / Claude Code / Continue
  AGENT/plugin/*.js    ← канонічні JS-плагіни для OpenCode

Чому так:

  1. Це назви з офіційних API самих оболонок, а не наш вибір.
     - Cline / Claude Code / Continue: механізм подій PreToolUse/
       PostToolUse офіційно називається "hooks" — це JSON-конфіг,
       який наказує оболонці запустити команду на подію
       (наприклад, hooks/Loops.json → python AGENT/scripts/anti_loop.py).
     - OpenCode: JSON-хуків узагалі немає. Розширення — це JS-модуль,
       який підписується на події (tool.execute.before тощо).
       Платформа називає це "plugin API" і АВТОМАТИЧНО завантажує
       усе з .opencode/plugins/ (множина). Папка hooks/ там не
       працювала б без ручного ключа "plugin" у opencode.json.

  2. У канонічному AGENT/ назви розділені за ТИПОМ виконавчого
     файлу, а не за платформою:
     - AGENT/hooks/ — JSON-хук-конфіги (Loops.json,
       watch_agent_file.json, str.translate.json,
       vercel_error_tracker.json). Скриптів там немає.
     - AGENT/plugin/ — канонічні JS-плагіни (anti-loop.js,
       startup.js), які manifest розповсюджує в .opencode/plugins/.
     - AGENT/scripts/ — самі Python-скрипти (anti_loop.py тощо),
       які й хуки, і плагіни лише ВИКЛИКАЮТЬ.

  3. Перейменування зламало б автозавантаження:
     - .opencode/plugins/ → hooks/: OpenCode перестав би бачити
       плагіни, повернулась би потреба в ручному конфізі.
     - AGENT/hooks/*.json → plugin/: зламалась би усталена
       термінологія решти чатів, manifest та документація.

========================================================================
ЧАСТИНА VII — РОЗПОВСЮДЖЕНІ SKILL-ФАЙЛИ В .github/skills/, .clinerules/skills/
========================================================================

17. SKILL.md (6 типів × 2 платформи = 12 файлів)
    
    Кожна навичка має дві копії:
      - .github/skills/<name>/SKILL.md
      - .clinerules/skills/<name>/SKILL.md
    
    Типи навичок:
      • context-management — Управління контекстом та анти-цикл механізми для локальних моделей 30-40B
      • errors             — Збір даних про помилки, взаємодію з інструкціями під час роботи
      • localization-qa    — Перевірка якості української локалізації
      • safe-edit          — Безпечне редагування файлів для слабших локальних моделей
      • session-history    — Створення та ведення історії сесій, дій та помилок
      • small-steps        — Адаптивна розбивка задач на кроки залежно від складності

========================================================================
ЧАСТИНА VIII — ДОДАТКОВІ ФАЙЛИ В AGENT/trash/ (архівні, не активні)
========================================================================

18. Тимчасові та архівні скрипти (не активні):
      • 2026-08-26_watch_agent_file.py          — Старий варіант watch_agent_file.py
      • 2026-08-28__tmp_migrate_events.py       — Тимчасовий скрипт міграції подій
      • 2026-08-28_migrate-to-central-agent.py  — Скрипт міграції до центрального репо (виконав своє)

========================================================================
ПІДСУМКОВА ТАБЛИЦЯ ВСІХ СКРИПТІВ
========================================================================

№   | Файл                               | Тип        | Критичний? | Призначення
----|------------------------------------|------------|------------|---------------------------
 1  | sync-agent.py                      | Python     | ✅ Так     | Синхронізація, agent-lock
 2  | update-manifest.py                 | Python     | ✅ Так     | Авто-генерація manifest
 3  | delete_to_trash.py                 | Python     | ⚠️ Необов. | Корзина для видалених файлів
 4  | install.ps1                        | PowerShell | ✅ Так     | Повна установка на Windows
 5  | install.sh                         | Bash       | ✅ Так     | Повна установка на Linux/macOS
 6  | test_install.ps1                   | PowerShell | ⚠️ Необов. | Тестування інсталятора
 7  | agent_startup.py                   | Python     | ✅ Так     | Запуск сервісів при старті
 8  | generate-agent-catalog.py          | Python     | ⚠️ Необов.| Генерація каталогу Агента
 9  | anti_loop.py                       | Python     | ✅ Так     | Анти-цикл логіка (канон)
10  | watch_agent_file.py                | Python     | ✅ Так     | Моніторинг файлів Агента
11  | str.translate.py                   | Python     | ✅ Так     | Переклад інтерфейсу
12  | .opencode/plugins/anti-loop.js      | JavaScript | ✅ Так     | Anti-hook перехоплення tool call'ів

========================================================================
КОРОТКІ КОМАНДИ ДЛЯ ПОВСЯКДЕННОЇ РОБОТИ
========================================================================

# Повна установка на Windows:
powershell -ExecutionPolicy Bypass -File agent_config\scripts\install.ps1

# Ручна синхронізація:
python agent_config/scripts/sync-agent.py --source <шлях_до_репо> --target . --apply

# Перевірка стану встановлених файлів:
python agent_config/scripts/sync-agent.py status --verbose

# Оновити існуючий проект:
python agent_config/scripts/sync-agent.py --update

# Видалити тільки Agent-файли (не чіпати проекту):
python agent_config/scripts/sync-agent.py remove [--force]

========================================================================
</content>
<parameter=filePath>
D:\GEN\Comfy-smart-lady-agent\agent_config\SCRIPTS_CATALOG.md