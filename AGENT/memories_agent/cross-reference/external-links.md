### Іврит THOT — словникові/морфологічні джерела (2026-09-07)
- **TBESH** (Translators Brief lexicon of Extended Strongs for Hebrew, STEPBible CC BY 4.0):
  словарні івритські леми для всіх Strong-кодів incl. службових H9xxx.
  Raw: `public/data/raw/LEXICONS/TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt`; конвертер: `scripts/buildThotStrongs.js`.
  URL: https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Lexicons/TBESH%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Hebrew%20-%20STEPBible.org%20CC%20BY.txt
- **TEHMC** (Translators Expansion of Hebrew Morphology Codes, STEPBible CC BY 4.0):
  розкодування FULL морф-кодів (OS/ETCBC-стиль: HR/Ncfsa, HVqp3ms...).
  Raw: `public/data/raw/LEXICONS/TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt`; мапа: `scripts/thotSblMorph.js`.
  URL: https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Morphology%20codes/TEHMC%20-%20Translators%20Expansion%20of%20Hebrew%20Morphology%20Codes%20-%20STEPBible.org%20CC%20BY.txt
- **Правила формату**: `AGENT/knowledge-base/hebrew-json-rules.md`
- **Генерація gen1**: `scripts/rebuildThotGen1.js` → `scripts/enrichThot.js`
- Нюанс TEHMC: `v` в V-кодах = **Imperative** (не Imperfect!); `w` = Consecutive Imperfect (wayyiqtol).

---


# 🔗 Крос-референс з memories/ (загальні процеси проекту)

## Дата створення
**2026-08-20 22:34** (отримано за шаблоном `python -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d %H:%M'))"`)

---

## 📌 Посилання на загальні процеси проекту memories/

Цей файл містить посилання на файли, які пов'язані із загальними процесами проекту memories (не тільки внутрішні історії агента). Коли агент створює записи, пов'язані із загальними процесами — фіксувати посилання тут.

---

### 📂 Структура memories/ (загальні процеси)
```
memories/
├── session/              # Загальна історія сесій проекту memories
│   └── session_YYYY-MM-DD.md
├── errors/               # Логи помилок та проблем проекту memories
│   ├── error-log_YYYY-MM-DD.md
│   └── anti-loop-records/
├── repo/                 # Журнал дій проекту memories
│   └── action-log_YYYY-MM-DD.md
└── knowledge-base/       # Загальна база знань
    └── base_YYYY-MM-DD.md
```

---

### 🔄 Взаємодія між memories_agent/ та memories/

| **Внутрішні історії агента** | **Загальні процеси проекту** |
|-----------------------------|------------------------------|
| `AGENT/memories_agent/session/session_YYYY-MM-DD.md` | `memories/session/session_YYYY-MM-DD.md` |
| `AGENT/memories_agent/errors/error-log_YYYY-MM-DD.md` | `memories/errors/error-log_YYYY-MM-DD.md` |
| `AGENT/memories_agent/actions/action-log_YYYY-MM-DD.md` | `memories/repo/action-log_YYYY-MM-DD.md` |

---

## 📝 Поточні записи крос-референс — ПОЛНИЙ ВІДПОВІДЬ

### Запис 1: Створення memories_agent/ та оновлення інструкції
**Час виконання:** 2026-08-20 22:34
**Тип запису:** ✅ Успішне створення структури внутрішньої історії агента, оновлення інструкції Comfy-smart-lady.md та прибирання зайвої папки knowledge-base/.

**Дія:**
- Створено структуру `memories_agent/` з усіма піддиректоріями: session/, errors/, actions/, config-changes/, cross-reference/ (без knowledge-base, бо вона вже існує в AGENT/knowledge-base/)
- Оновлено `AGENT/agents/Comfy-smart-lady.md`: замінено всі посилання з `memories/` на `AGENT/memories_agent/` та додано розділ крос-референс

**Посилання:**
- Інструкція: `AGENT/agents/Comfy-smart-lady.md` — оновлена
- Структура: `AGENT/memories_agent/session/, AGENT/memories_agent/errors/, AGENT/memories_agent/actions/, AGENT/memories_agent/config-changes/, AGENT/memories_agent/cross-reference/`
- Міграція: `AGENT/memories_agent/migration-note.md` — містить опис структури та правил використання

**Результат:** ✅ Структура створена, інструкція оновлена з крос-референсом.
**Час фіксації:** 2026-08-20 22:34

---

### Запис 2: Стан на поточний момент — ПОЛНИЙ ВІДПОВІДЬ
**Час виконання:** 2026-08-20 22:34
**Тип запису:** ✅ План повністю виконано, зайву папку knowledge-base прибрано.

**Статус сесії:** в процесі ведення внутрішньої історії Агента
**Останнє оновлення:** 2026-08-20 22:34

✅ **Структура memories_agent/ повністю створена**
✅ **Всі файли заповнені та оновлені**
✅ **Зайву папку knowledge-base прибрано, інструкції приведено до правильної структури.**

---

### Запис 3: Перенесення внутрішніх подій з memories/errors/ (2026-08-22 18:00)
**Час виконання:** 2026-08-22 18:00
**Тип запису:** ✅ Перенесення внутрішніх помилок агента з `memories/errors/` до `AGENT/memories_agent/errors/`.

**Дія:**
- Створено `AGENT/memories_agent/errors/error-log_2026-08-13.md` — EXACT REPEAT цикли #10 і #11
- Створено `AGENT/memories_agent/errors/error-log_2026-08-18.md` — помилка переміщення `.memories/`
- Створено `AGENT/memories_agent/errors/error-log_2026-08-21.md` — помилки search_web (404) та fetch_url_content (401)
- Переписано `AGENT/memories_agent/actions/action-log_2026-08-22.md` з правильним кодуванням UTF-8

**Посилання:**
- Внутрішні: `AGENT/memories_agent/errors/error-log_2026-08-13.md`, `error-log_2026-08-18.md`, `error-log_2026-08-21.md`, `actions/action-log_2026-08-22.md`
- Зовнішні (джерела): `memories/errors/error-log_2026-08-13.md`, `error-log_2026-08-18.md`, `error-log_2026-08-21.md`

**Результат:** ✅ Внутрішні події перенесено, оригінали збережено в `memories/` для історичного аудиту.
**Час фіксації:** 2026-08-22 18:02

---

### Запис 4: Перенесення внутрішніх подій за 2025-12-24 (2026-08-22 18:40)
**Час виконання:** 2026-08-22 18:40
**Тип запису:** ✅ Перенесення внутрішніх подій агента (ініціальна сесія, помилки search_web) з `memories/` до `AGENT/memories_agent/`.

**Дія:**
- Створено `AGENT/memories_agent/errors/error-log_2025-12-24.md` — помилки search_web (404), fetch_url_content (401)
- Створено `AGENT/memories_agent/actions/action-log_2025-12-24.md` — ініціалізація сесії, завантаження інструкцій
- Створено `AGENT/memories_agent/session/session_2025-12-24.md` — ініціальна сесія агента
- Очищено `memories/errors/error-log_2026-08-20.md` — видалено звичайну подію (успішне створення файлів), яка не є помилкою

**Посилання:**
- Внутрішні: `AGENT/memories_agent/errors/error-log_2025-12-24.md`, `actions/action-log_2025-12-24.md`, `session/session_2025-12-24.md`
- Зовнішні (джерела): `memories/errors/error-log_2025-12-24.md`, `memories/repo/action-log_2025-12-24.md`, `memories/session/session_2025-12-24.md`

**Результат:** ✅ Внутрішні події перенесено, оригінали збережено в `memories/` для історичного аудиту.
**Час фіксації:** 2026-08-22 18:40

---

## 🔄 Поточний стан
**Статус записів:** в процесі ведення внутрішньої історії Агента
**Останнє оновлення:** 2026-08-22 18:02

Цей файл фіксує крос-референси між внутрішньою історією агента та загальними процесами проекту memories.
- Створено `AGENT/memories_agent/actions/action-log_2025-12-24.md` — ініціалізація сесії, завантаження інструкцій
- Створено `AGENT/memories_agent/session/session_2025-12-24.md` — ініціальна сесія агента
- Очищено `memories/errors/error-log_2026-08-20.md` — видалено звичайну подію (успішне створення файлів), яка не є помилкою

**Посилання:**
- Внутрішні: `AGENT/memories_agent/errors/error-log_2025-12-24.md`, `actions/action-log_2025-12-24.md`, `session/session_2025-12-24.md`
- Зовнішні (джерела): `memories/errors/error-log_2025-12-24.md`, `memories/repo/action-log_2025-12-24.md`, `memories/session/session_2025-12-24.md`

**Результат:** ✅ Внутрішні події перенесено, оригінали збережено в `memories/` для історичного аудиту.
**Час фіксації:** 2026-08-22 18:40

---

### ?? ������� 5: release-readiness-plan.md execution (2026-08-22 21:15)
**��� ���������:** 2026-08-22 21:15
**��� ������:** ? ????????? ????. ?? ?? 6 ????? ?? **AGENT/release-readiness-plan.md**, ???? ????. .opencode/node_modules/ ??? ?????, ??? ???? ????.

**?�:**
- ???? A: .gitignore ???? ???? ?? ???? ???? ???? ?? ?? git check-ignore
- ???? B: ??????? __pycache__/, .opencode/package-lock.json ????; npm install ??? 27 packages; .opencode/node_modules/@opencode-ai/plugin ???? True
- ???? C: /AGENT/agents, /AGENT/skills ??? Test-Path True
- ???? D: python scripts/sync-agent.py --dry-run --source . ??? ???? ????
- ???? E: Python (7/0), JSON (12/1), JS, Catalog (75 files) ???
- ???? F: git status --short ??? ?? ???? ????

**??ᨫ����:**
- AGENT/memories_agent/actions/action-log_2026-08-22.md - ???? ?? A-F ??? ????
- AGENT/memories_agent/session/session_2026-08-22.md - ?? ???? ???? ????
- .gitignore ?? ???? .opencode/node_modules/ rule

**???????:** ? ?????? ?? ???? ???? ?? ???? ????, ???? ???? npm install ??? ????.
**��� ?????:** 2026-08-22 21:15


## Крос-референси після міграції (2026-08-28)
| Подія агента | Джерело в memories/ | Призначення в memories_agent/ |
|---|---|---|
| Автозавантаження агента, .continue (2026-08-18) | memories/session/session_2026-08-18.md | session/session_2026-08-18.md |
| Нормалізація шляхів + фікс anti-loop (2026-08-14) | memories/session/session_2026-08-14.md | actions/action-log_2026-08-14.md |
| Створення центрального репо (2026-08-20 19:08) | memories/session/session_2026-08-20.md | actions/action-log_2026-08-20.md |
| Модель чатів-інтерпретаторів (2026-08-20 14:41) | memories/session/session_2026-08-20.md | actions/action-log_2026-08-20.md |
| Інтеграція V3 (2026-08-26) | memories/session/session_2026-08-26.md; memories/repo/action-log_2026-08-26.md | session/session_2026-08-26.md; actions/action-log_2026-08-26.md |
| Аудит + stub-конвертація (2026-08-28) | memories/session/session_2026-08-28.md; memories/repo/action-log_2026-08-28.md | actions/action-log_2026-08-28.md |
| 2026-08-28 | memories/repo/action-log_2026-08-18.md | session/session_2026-08-18.md | переносення журналу про автозавантаження агента |

## 📅 2026-09-05 — Робота над бібліотекою перекладів + плутанина історій

### Запис 6: Бібліотека перекладів GEN 1 / MAT 1 (2026-09-05 21:13–22:50)
**Тип запису:** ✅ Основна проєктна робота дня.

**Дія:**
- Докучано недостаючі raw: UBT GEN1 (31 в.), UBT MAT1 (25 в.), KHOMENKO GEN1 (31 в.) з ukrbible.at.ua
- Систематизовано підбір слів → Strong (scripts/strongLexicon.js, ~250 термінів; семантичний крок в alignVerse)
- Чистка THOT raw: 149 злеплених токенів (scripts/fixThotSlashes.js)
- Усі 16 файлів GEN1/MAT1 повні та валідні (покриття strongs 95–100%)
- Зафіксовано джерела парсингу: memories_Under-word-app/knowledge-base/bible-library-sources.md (переміщено з AGENT/knowledge-base/ 2026-09-07 — проєктне знання, не агентське)

**Посилання:** проєктна історія `memories_Under-word-app/session/session_2026-09-05.md`; агентська `AGENT/memories_agent/session/session_2026-09-05.md`.
**Результат:** ✅ Бібліотека GEN1/MAT1 сформована; вирівнювання слів до Strong систематизовано.
**Час фіксації:** 2026-09-05 23:15

---

### Запис 7: Виправлення плутанини історій (2026-09-05 23:15)
**Тип запису:** ✅ Виправлено — проєктні події були в агентському файлі.

**Дія:** за вказівкою користувача агентський файл переписано як справді внутрішній (помилки скриптиів, недоступність web_search, плутанина); проєктні події залишені в memories_Under-word-app/session/.
**Результат:** ✅ Розділення відновлено.
**Час фіксаціці:** 2026-09-05 23:15
