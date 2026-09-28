# BUG‑001: `sync-agent.py` блокує інсталяцію — `ManifestParser.parse()` хибно стирає `//` у URL

> **Статус:** 🚧 Підтверджена, блокує всі варіанти інсталяції (Спосіб A `install.ps1` і Спосіб B `sync-agent.py --apply`).
> **Джерело істини:** `agent_config/manifest.json` (центральне репо) — **валідний JSON, не пошкоджений**.
> **Бага в коді, а не в даних.**

## TL;DR

`ManifestParser.parse()` у `agent_config/scripts/sync-agent.py` (рядки 61–64) перед `json.loads` видаляє `//`‑коментарі **без розуміння, чи знаходяться всередині JSON‑рядка**. Оскільки `manifest.json` містить URL‑и типу `https://...`, під `//` потрапляє **вміст URL**, разом із закривальною лапкою `"`. Результат — `json.loads` бачить незавершений рядок, в який потрапляє `\n` → **`Invalid control character`**. Встановлення не стартує; користувач не може жодним чином інсталювати агента.

---

## 1. Де

- **Файл:** `agent_config/scripts/sync-agent.py`
- **Клас/функція:** `ManifestParser.parse()`
- **Рядки:** 61–64 (правило/коментар) та 67 (`return json.loads(cleaned_content)`)
- **Канонічний шлях до manifest:** `<repo>/agent_config/manifest.json`

### Відповідні рядки (локація `parse()`):

```python
61  # Видалити коментарі Python/C-стилю за допомогою регулярних виразів
62  # Цей шаблон знаходить // або /* */ коментарі і замінює їх на пробіл
63  cleaned_content = re.sub(r'//.*?(?=\n|$)', '', content)        # Single-line // коментарі
64  cleaned_content = re.sub(r'/\*[\s\S]*?\*/', '', cleaned_content) # Multi-line /* */ коментарі
...
67  return json.loads(cleaned_content)
```

---

## 2. Корінь

1. `manifest.json` **є коректним JSON** (перевірено `json.loads(open(path,'rb').read())` → `OK`, `control chars = 0`).
2. У `manifest.json` є рядки з URL, де `//` — це **не коментар**, а частина значення:
   ```text
   6:   "repo_url": "https://raw.githubusercontent.com/ordercomplete/Comfy-smart-lady-agent/main/agent_config/VERSION",
   7:   "git_url":  "https://github.com/ordercomplete/Comfy-smart-lady-agent.git",
   ```
3. Регексп `re.sub(r'//.*?(?=\n|$)', '', content)` шукає **будь‑де** `//` і стирає до кінця рядка. Для рядка 6 він збігається з `//raw.githubusercontent.com/.../VERSION",` — тобто стирає **частину URL плюс закривальну `"` та кому `,`**.
4. Після стирання рядок 6 перетворюється на:
   ```text
   "repo_url": "https:
   ```
   — рядок‑значення **не завершений** (відкрита `"`).
5. `json.loads` читає далі, рядок продовжується по нових рядках, доки не натрапить на лінійний розрив `\n` всередині рядка → **`Invalid control character at: line 6 column 28 (char 141)`**.

### Доказ (reproduced):

```text
--- line 6 (raw)      : "repo_url": "https://raw.githubusercontent.com/ordercomplete/Comfy-smart-lady-agent/main/agent_config/VERSION",
--- line 6 (cleaned)  : '        "repo_url": "https:'
--- line 7 (cleaned)  : '        "git_url": "https:'
REPRODUCED ERROR: Invalid control character at: line 6 column 28 (char 141)
```

Повідомлення в консолі користувача (від `sync-agent.py`, рядок 69):

```text
❌ Помилка парсингу manifest.json: Invalid control character at: line 6 column 28 (char 141)
```

---

## 3. Як відтворити (100% стабільно)

```powershell
# 1) Свіжий клон центрального репо
git clone https://github.com/ordercomplete/Comfy-smart-lady-agent.git "$env:TEMP\csl-agent"

# 2) Любий dry-run (навіть без .gitignore/.opencode тощо у цільному)
cd D:\GEN\LLM-info
python "$env:TEMP\csl-agent\agent_config\scripts\sync-agent.py" `
    --source "$env:TEMP\csl-agent" --target . --dry-run
```

**Очікуваний результат:** список `📋 [DRY-RUN] Скопіювати: ...`.
**Фактичний результат:** керівне `sys.exit(1)` з повідомленням про парсинг `manifest.json` вище.

> ⚠️ Ця ж помилка виникає у **Спосіб A** (`install.ps1` → `python …\sync-agent.py --source $TmpDir --target . --dry-run`), бо `install.ps1` клонує той самий репо і використовує той самий `sync-agent.py`.

---

## 4. Вплив

| Сфера | Вплив |
|-------|-------|
| Інсталяція нового проєкту | 🚫 Повністю зламана (обидва способи A і B). |
| Оновлення існуючого | 🚫 `--update` / `--pull --apply` також зламані. |
| `manifest.json` | Дані коректні; пошкодження ледь у тимчасовій копії в пам’яті під час парсингу. |

---

## 5. Вимоги до виправлення (обмеження, які неможна порушити)

1. `manifest.json` — **джерело істини**, валідні URL з `https://` рятувати неможна. Люба логіка має бути **контекст‑свідомою**.
2. `sync-agent.py` має залишитися **залежним тільки від стандартної бібліотеки** (стандартний `json`). Додавати зовнішні пакети (`json5`, `jsonc`) **не рекомендується** — це розбиває «нічого не ставимо» інсталятор.
3. `parse()` повинен **продовжувати підтримувати** `//`‑ та `/* */`‑коментарі (це задумання: “з підтримкою коментарів”, бач. docstring рядка 57).
4. Після виправлення `--dry-run` має працювати, а `--apply` — копіювати файли згідно `manifest.json`.

---

## 6. Рекомендоване виправлення

Найнадійніший міні‑токенізатор: створити функцію `strip_jsonc_comments(content)`, яка видаляє `//` та `/* */` лише **поза межами рядків** (тобто з урахуванням `"` та екранування `\"`). Це легко тестується й не додає залежностей.

### Заміна рядків 61–64

```python
def _strip_jsonc_comments(content: str) -> str:
    """Видаляє // та /* */ коментарі, не торкаючись рядків-значень JSON.

    Рядки починаються з " і закінчуються наступною неекранованою ".
    \" поза рядком не завершує рядок.
    """
    out = []
    i = 0
    n = len(content)
    in_str = False
    while i < n:
        c = content[i]
        if in_str:
            out.append(c)
            if c == '\\' and i + 1 < n:           # екранування наступного символу
                out.append(content[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        # поза рядком
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < n and content[i + 1] == '/':
            i += 2
            while i < n and content[i] not in '\r\n':
                i += 1
            continue
        if c == '/' and i + 1 < n and content[i + 1] == '*':
            i += 2
            while i + 1 < n and not (content[i] == '*' and content[i + 1] == '/'):
                i += 1
            i += 2  # пропустити */
            continue
        out.append(c)
        i += 1
    return ''.join(out)
```

### Оновлення `parse()` (рядки 56–70)

```python
def parse(self) -> dict:
    """Завантажити та проаналізувати manifest.json (з підтримкою коментарів)."""
    with open(self.manifest_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Видаляти коментарі ПОЗА межами JSON‑рядків (безпечно для URL типу https://)
    cleaned_content = _strip_jsonc_comments(content)

    try:
        return json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print(f"❌ Помилка парсингу manifest.json: {e}")
        sys.exit(1)
```

---

## 7. Перевірка після виправлення

```powershell
# DRY-RUN має працювати без помилки:
python "$env:TEMP\csl-agent\agent_config\scripts\sync-agent.py" --source "$env:TEMP\csl-agent" --target . --dry-run
# Очікується: список дій  📋 [DRY-RUN] Скопіювати / Створити stub
```

```python
# Автоперевірка (один рядок) має давати OK без зміни manifest.json:
python -c "import json,re; c=open('agent_config/manifest.json',encoding='utf-8-sig').read(); json.loads(_strip_jsonc_comments(c)); print('JSON OK after strip')"
```

---

## 8. Примітки для фіксера

- `manifest.json` **не треба** редагувати — він валідний. Усього потрібно виправити `parse()` у `sync-agent.py`.
- Після виправлення `agent_config/manifest.json` має бути **скопійований** у цільовий проект у складі `--apply` (дія `copy_full`), бо він є одним із `files` у манифесті.
- Переконайтесь, що `install.ps1` та `install.sh` використовують цей же `sync-agent.py` (вони так роблять — бач. `install.ps1`, кроки 3–4) → фікс один раз лікує обидва способи.
- Рекомендується додати тест (unit чи `test_install.ps1`), що маніфест парситься успішно навіть тоді, коли містить `https://`.

---

*Запис створено як BUG‑001 для агента‑фіксера. Пов’язаний файл: `agent_config/scripts/sync-agent.py` (функція `ManifestParser.parse`).*