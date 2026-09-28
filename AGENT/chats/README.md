# 📱 Чотири чати (платформи) — загальний огляд

**Останнє оновлення:** 2026-08-22 17:55

Агент **Comfy-smart-lady** інтегрований у чотири платформи (чати), де він працює:

| Платформа | Каталог у проєкті | Тип | Офіційний сайт |
|-----------|-------------------|-----|----------------|
| **Cline** | `.clinerules/` | VS Code розширення (IDE-агент) | https://cline.bot |
| **OpenCode** | `.opencode/` | CLI coding-агент (термінал) | https://opencode.ai |
| **GitHub Copilot** | `.github/` | Вбудований AI-асистент (VS Code / GitHub) | https://github.com/features/copilot |
| **Continue** | `.continue/` | VS Code розширення (open-source AI агент) | https://continue.dev |

---

## 📊 Зведена таблиця рейтингів та завантажень (2026-08-22)

| Платформа | ⭐ Рейтинг | Кількість оцінок | 📥 Встановлень (VS Code) | 🌟 GitHub зірок | 🍴 GitHub форків | Версія | Ліцензія | Ціна |
|-----------|-----------|------------------|--------------------------|-----------------|------------------|--------|----------|------|
| **Cline** | ⭐ 4.06/5 | 312 | 5 063 329 | 66 648 | 7 183 | 4.1.12 | Apache-2.0 | Free |
| **OpenCode** | — (CLI) | — | — | 200 213 | 25 857 | dev | MIT | Free (open-source) |
| **GitHub Copilot** | ⭐ 4.08/5 | 1 054 | 74 421 021 | — (закритий) | — | 1.388.0 | Proprietary | Trial (платний) |
| **Continue** | ⭐ 3.27/5 | 180 | 3 971 652 | 35 589 | 5 269 | 2.1.0 | Apache-2.0 | Free |

> **Джерела:** VS Code Marketplace API, GitHub REST API (станом на 2026-08-22).

---

## 📄 Окремі файли з детальним описом

- [**Cline** → `AGENT/chats/cline/README.md`](cline/README.md)
- [**OpenCode** → `AGENT/chats/opencode/README.md`](opencode/README.md)
- [**GitHub Copilot** → `AGENT/chats/github-copilot/README.md`](github-copilot/README.md)
- [**Continue** → `AGENT/chats/continue/README.md`](continue/README.md)

---

## 🔗 Корисні посилання (загальні)

| Платформа | Marketplace | GitHub | Документація |
|-----------|-------------|--------|--------------|
| **Cline** | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) | [github.com/cline/cline](https://github.com/cline/cline) | [cline.bot](https://cline.bot) |
| **OpenCode** | — (CLI) | [github.com/anomalyco/opencode](https://github.com/anomalyco/opencode) | [opencode.ai](https://opencode.ai) |
| **GitHub Copilot** | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) | [GitHub Features](https://github.com/features/copilot) | [docs.github.com/copilot](https://docs.github.com/copilot) |
| **Continue** | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Continue.continue) | [github.com/continuedev/continue](https://github.com/continuedev/continue) | [continue.dev](https://continue.dev) |

---

## 🎯 Як інтегровані чати в агенті

Агент визначає, у якому додатку працює, і завантажує відповідні скрипти (див. `AGENT/agents/Comfy-smart-lady.md`, розділ «Завантаж потрібні файли скриптів»):

1. **Якщо це `.github`** (GitHub Copilot) → завантажує `AGENT/scripts/anti_loop.py`
2. **Якщо це `.opencode`** (OpenCode) → завантажує `.opencode/plugins/anti-loop.js`, потім `AGENT/scripts/anti_loop.py`
3. **Якщо це `.clinerules`** (Cline) → завантажує `.clinerules/hooks/Loops.json`, потім `AGENT/scripts/anti_loop.py`
4. **Якщо це `.continue`** → має власну структуру з `hooks/Loops.json`, `prompts/system-prompt.md`, `agents/`

---

## 🏷️ Чому в `.opencode` — «плагіни», а в інших чатах — «хуки»?

Різні назви папок — це **не розсинхрон**, а свідоме наслідування конвенцій кожної платформи при єдиному канонічному ядрі:

```
AGENT/scripts/*.py   ← єдине джерело виконання (для всіх чатів)
AGENT/hooks/*.json   ← хук-конфіги для Cline / Claude Code / Continue
AGENT/plugin/*.js    ← канонічні JS-плагіни для OpenCode
```

**Чому так:**

1. **Це назви з офіційних API самих оболонок, а не наш вибір.**
   - *Cline / Claude Code / Continue:* механізм подій `PreToolUse`/`PostToolUse` офіційно називається **hooks** — це JSON-конфіг, який наказує оболонці запустити команду на подію (наприклад, `hooks/Loops.json` → `python AGENT/scripts/anti_loop.py`).
   - *OpenCode:* JSON-хуків узагалі немає. Розширення — це JS-модуль, який підписується на події (`tool.execute.before` тощо). Платформа називає це **plugin API** і *автоматично* завантажує усе з `.opencode/plugins/` (множина). Папка `hooks/` там не працювала б без ручного ключа `plugin` у `opencode.json`.

2. **У канонічному `AGENT/` назви розділені за типом виконавчого файлу, а не за платформою:**
   - `AGENT/hooks/` — JSON-хук-конфіги (`Loops.json`, `watch_agent_file.json`, `str.translate.json`, `vercel_error_tracker.json`). Скриптів там немає — тільки виконавчі конфіги.
   - `AGENT/plugin/` — канонічні JS-плагіни (`anti-loop.js`, `startup.js`), які manifest розповсюджує в `.opencode/plugins/`.
   - `AGENT/scripts/` — самі Python-скрипти (`anti_loop.py` тощо), які й хуки, і плагіни лише **викликають**.

3. **Перейменування зламало б автозавантаження:**
   - `.opencode/plugins/` → `hooks/`: OpenCode перестав би бачити плагіни — повернулась би потреба в ручному конфізі.
   - `AGENT/hooks/*.json` → `plugin/`: зламалась би усталена термінологія решти чатів, manifest та документація.

---

*Цей файл є частиною централізованого реєстру `AGENT/chats/` — бази знань про чотири платформи, де працює агент Comfy-smart-lady.*