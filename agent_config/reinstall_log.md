# Reinstall Log — Перевстановлення Агента (factory reset)

**Дата створення:** 31 серпня 2026  
**Версія функціоналу:** 1.5.0  

---

## Проблема (що було до reinstall)

Згідно з попередніми спробами перевстановлення:

| # | Проблема | Наслідок |
|---|----------|----------|
| 1 | `sync-agent.py remove` → корзина, а не `unlink` | Файли залишаються в `AGENT/trash/` та `trash/`. Для чистого інсталятора це зайвий шум. |
| 2 | `install.ps1` потрапив у `AGENT/trash/` | Інсталятор сам потрапляє у корзину під час `remove`, оскільки є файлом `agent_config/`. Після `remove` його немає — неможливо повторно запустити. |
| 3 | 4 файли пропущено (Skipped: 4 files modified) | Без `--force` модифіковані файли не видаляються. Для чистого інсталяції це ризик — залишаються старі файли. |
| 4 | Після `remove` lock-файл видаляється | Другий `remove --force` нічого не робить (`"No agent-lock.json found"`). Неможливо ітераційно очистити. |
| 5 | `--pull` падає без `./repos/Comfy-smart-lady-agent/` | Команда очікує локальний клон, а не клонує автоматично. |

---

## Рішення: новий режим перевстановлення

### A. Код

**1. Підкоманда `reinstall` у `sync-agent.py`**
```bash
python agent_config/scripts/sync-agent.py reinstall [--source <url>] [--dry-run]
```

**4 етапи:**

| Етап | Дія | Деталі |
|------|-----|--------|
| 1/4 | **Purge** | Повне видалення ВСІХ файлів Агента згідно `manifest.json` + `AGENT_DIRS`. Використовує `--force` для модифікованих файлів. Бypass trash — файли видаляються назавжди через `Path.unlink()`. |
| 2/4 | **Source** | Визначення джерела: якщо `--source` не вказаний або не існує локально → авто-клон з GitHub (`https://github.com/ordercomplete/Comfy-smart-lady-agent.git`). |
| 3/4 | **Install** | Запуск `sync-agent.py --apply` з тимчасового/локального джерела. Копіює ядро AGENT/, файли manifest, root_files, stub-файли. Створює новий `agent-lock.json`. |
| 4/4 | **Verify** | Запуск: `gitignore` → `status --verbose` → `py_compile` всіх критичних файлів (anti_loop.py, watch_agent_file.py, str.translate.py, agent_startup.py, delete_to_trash.py, sync-agent.py). |

**2. Прапор `--purge` для `remove`**
```bash
python agent_config/scripts/sync-agent.py remove --purge [--force]
```
- Якщо `--purge` встановлено: файли видаляються **безповоротно** (через `Path.unlink()`), а не через `delete_to_trash.py`.
- `trash/` та `AGENT/trash/` очищаються після purge, створюються нові порожні з `.gitignore`.

**3. Авто-клон `--source`**
- Якщо `--source` не вказаний, а `--pull` не працює (немає локального клону): скрипт тимчасово клонує центральне репо через `git clone --depth 1 <repo_url> <temp>`, використовує його, потім видаляє.

### B. Інструкції

**4. Використання reinstall**
```bash
# Dry-run — перевірити що станеться (без змін)
python agent_config/scripts/sync-agent.py reinstall --dry-run

# Повне перевстановлення з GitHub (авто-клон)
python agent_config/scripts/sync-agent.py reinstall

# Перевстановлення з локального репо
python agent_config/scripts/sync-agent.py reinstall --source ~/repos/Comfy-smart-lady-agent

# З примусовим видаленням модифікованих файлів (автоматично)
python agent_config/scripts/sync-agent.py reinstall --force
```

**5. Рекомендації**
- **Завжди запускайте `--dry-run` спочатку**, щоб побачити які файли будуть видалені/змінені.
- **Бэкапуйте модифіковані файли вручну**, якщо вони містять важливі зміни (reinstall видаляє ВСІ Agent-файли без винятків).
- **Перевіряйте `status --verbose` після reinstall** — це гарантує, що всі файли на місці.

---

## Історія змін

### 2026-08-31 — Версія 1.5.0 (нова функція)
- Додано підкоманду `reinstall` у `sync-agent.py`.
- Додано прапор `--purge` для `remove`.
- Виправлено CLI dispatch: тепер `reinstall` підтримує `--dry-run` / `-n`.
- Верифіковано: `reinstall --dry-run` exit 0, повний `reinstall` exit 0 (4/4 етапи OK).

---

## Тестовий чекліст

| # | Перевірка | Статус |
|---|-----------|--------|
| 1 | `reinstall --dry-run` — exit 0, показує purge + джерело | ✅ ОК |
| 2 | Повний `reinstall` — 4/4 етапи проходять успішно | ✅ ОК (перевірено 31.08.2026) |
| 3 | `remove --purge` — файли видаляються без Корзини, trash очищується | ✅ ОК |
| 4 | `reinstall --source <url>` — авто-клон з GitHub працює | ✅ ОК (перевірено під reinstall) |
| 5 | py_compile всіх критичних файлів після reinstall — exit 0 | ✅ ОК |

---

## Архітектура (посилання на код)

- **sync-agent.py**: функції `cmd_reinstall()`, `_resolve_reinstall_source()`, `cmd_remove(..., purge=True)`
- **delete_to_trash.py**: використовується при `remove` без `--purge` для маршрутизації файлів у корзину
- **manifest.json**: джерело правди для всіх target_paths (файли Агента)
