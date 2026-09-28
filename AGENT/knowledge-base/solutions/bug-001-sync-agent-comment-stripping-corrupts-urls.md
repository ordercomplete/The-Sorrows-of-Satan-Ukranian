# BUG-001: ManifestParser.parse() хибно стирає `//` у URL через regex

## Проблема

`sync-agent.py` (функція `ManifestParser.parse()`) використовує regex для strip‑інгу `//`‑коментарів із JSON **перед** `json.loads`. Оскільки `manifest.json` містить URL типу `https://...`, regex збігається з `//` у середині URL, стирає залишок рядка разом із закривальною лапкою `"`, що руйнує JSON → `Invalid control character at: line 6 column 28 (char 141)`. Це блокує всю інсталяцію (`install.ps1`, `sync-agent.py --dry-run/--apply/--update`).

## Контекст

- **Файл:** `agent_config/scripts/sync-agent.py`
- **Клас/функція:** `ManifestParser.parse()` (колишні рядки 61–64)
- **Джерело даних:** `agent_config/manifest.json` — валідний JSON, не пошкоджений. `manifest.json` має рівно 2 входження `//`, обидва у URL (`https://`).
- **Спільна помилка:** regex `re.sub(r'//.*?(?=\n|$)', '', content)` не розрізняє рядки JSON та коментарі.

## Рішення

Замінити regex на **контекстно‑свідомий токенізатор** `_strip_jsonc_comments()`, який видаляє `//` та `/* */` **лише поза межами JSON‑рядків** (з урахуванням екранування `\"`). Це працює лише на стандартній бібліотеці (`json`), без зовнішніх залежностей.

```python
def _strip_jsonc_comments(content: str) -> str:
    """Видаляє // та /* */ коментарі, не торкаючись рядків-значень JSON."""
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
        if c == '"':                              # вхід у рядок
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < n and content[i + 1] == '/':   # // коментар
            i += 2
            while i < n and content[i] not in '\r\n':
                i += 1
            continue
        if c == '/' and i + 1 < n and content[i + 1] == '*':   # /* */ коментар
            i += 2
            while i + 1 < n and not (content[i] == '*' and content[i + 1] == '/'):
                i += 1
            i += 2  # пропустити */
            continue
        out.append(c)
        i += 1
    return ''.join(out)
```

У `parse()` замінюються `re.sub`‑виклики на `cleaned_content = _strip_jsonc_comments(content)`. Топ‑рівневий `import re` видаляється (використовувався лише для цього regex; інші функції використовують локальні `import re as _re`).

## Перевірка

- `py_compile` — OK.
- `test_manifest_parsing.py` — 6 unit‑тестів: URL preserved, `//` comment stripped outside string, `/* */` outside/inside string, escaped quote, реальний manifest.json, `ManifestParser.parse()`.
- `--dry-run` — працює без помилок, виводить список копіювання та створення stub.

## Дата та статус

**Дата:** 2026-08-28 20:59. **Статус:** ✅ Виправлення застосовано до `agent_config/scripts/sync-agent.py`. `test_manifest_parsing.py` додано до `agent_config/scripts/`. `manifest.json` не редагувався.
