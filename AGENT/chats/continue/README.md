# 🤖 Continue — open-source AI coding-агент

**Останнє оновлення:** 2026-08-22 17:55

---

## 📊 Рейтинг та завантаження

| Метрика | Значення | Джерело |
|---------|----------|---------|
| 📥 Встановлень (VS Code) | **3 971 652** | VS Code Marketplace API |
| ⭐ Рейтинг | **3.27 / 5** (180 оцінок) | VS Code Marketplace API |
| 📦 Версія | **2.1.0** (оновлено 2026-06-19) | VS Code Marketplace API |
| 🌟 GitHub зірок | **35 589** | GitHub API |
| 🍴 GitHub форків | **5 269** | GitHub API |
| 🗓️ Дата публікації | 2023-05-27 | VS Code Marketplace API |
| 🏷️ Ліцензія | Apache-2.0 | GitHub API |
| 💰 Ціна | **Free (open-source)** | VS Code Marketplace |
| 📝 Опис | "The leading open-source AI code agent" | VS Code Marketplace API |
| 💬 Мова | TypeScript | GitHub API |
| 🐛 Відкриті issues | 936 | GitHub API |
| 👥 Підписники | 163 | GitHub API |
| 🏠 Сайт | https://continue.dev | GitHub API |

---

## 🔧 Опис функціоналу

**Continue** — open-source AI coding-агент, який працює як розширення для VS Code та JetBrains IDE.

- ✅ **Чат з AI** — діалог з будь-якою LLM (OpenAI, Anthropic, Gemini, локальні моделі)
- ✅ **Автодоповнення коду** — inline-підказки під час написання
- ✅ **Автономний агент** — виконує задачі в коді з дозволу користувача
- ✅ **Контекст проєкту** — підключення документації, файлів, кодбейзу (RAG)
- ✅ **Підтримка локальних моделей** — Ollama, LM Studio, vLLM, llama.cpp
- ✅ **Конфігурація через YAML** — `config.json`, `permissions.yaml`, `agents/`, `hooks/`, `prompts/`
- ✅ **Плагіни** — розширення функціоналу
- ✅ **Режим headless / CLI** — через інструмент `continue` CLI
- ✅ **Правила та інструкції** — `.continueinstruct`, `system-intro.md`, системні промпти

---

## 🎯 Переваги

- 🌐 **Повністю open-source** — Apache-2.0, можна форкнути та доопрацювати
- 💻 **Підтримка локальних моделей** — безкоштовна робота без хмари
- 🔌 **Гнучке налаштування** — `config.json`, `agents/`, `hooks/` (Loops.json), `prompts/`
- ⚡ **Швидка інтеграція** — VS Code + JetBrains
- 🚀 **Найбільший open-source конкурент** Cline серед IDE-агентів
- 🧠 **Контекст кодбейзу** — RAG-пайплайн для великих проєктів

---

## ⚠️ Недоліки

- ⚠️ **Рейтинг нижче конкурентів** — 3.27/5 (у Cline 4.06, у Copilot 4.08)
- ⚠️ **Менша кількість встановлень** — 3.9 млн проти 5 млн у Cline, 74 млн у Copilot
- ⚠️ **Автономність менш зріла** — агент-режим розвивається повільніше
- ⚠️ **Менше зірок на GitHub** — 35.5K проти 66.6K у Cline
- ⚠️ **Конфігурація складніша** — YAML/JSON налаштування може лякати новачків

---

## 🔗 Посилання

| Ресурс | URL |
|--------|-----|
| 🌐 Офіційний сайт | https://continue.dev |
| 📦 VS Code Marketplace | https://marketplace.visualstudio.com/items?itemName=Continue.continue |
| 🐙 GitHub | https://github.com/continuedev/continue |
| 🐛 Issues | https://github.com/continuedev/continue/issues |
| 📖 Документація | https://docs.continue.dev (через сайт) |

---

## 🤝 Інтеграція з агентом Comfy-smart-lady

У проєкті Continue використовує каталог **`.continue/`**:

- `.continue/agents/Comfy-smart-lady.md` — канонічний файл агента
- `.continue/hooks/Loops.json` — anti-loop конфігурація
- `.continue/prompts/system-prompt.md` — системний промпт
- `.continue/config.json` — основна конфігурація розширення
- `.continue/permissions.yaml` — дозволи для виконання команд
- `.continue/system-intro.md` — вступна інструкція
- `.continue/.continueinstruct` — додаткові інструкції
- `.continue/CONTINUE_INTEGRATION_PLAN.md` — план інтеграції Continue
- `.continue/agents/new-config.yaml` — конфігурація агента

---

*Цей файл — частина реєстру `AGENT/chats/`. Джерела даних: VS Code Marketplace API, GitHub API (2026-08-22).*