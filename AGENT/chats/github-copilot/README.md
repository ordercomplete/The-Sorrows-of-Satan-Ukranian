# 💜 GitHub Copilot — вбудований AI-асистент

**Останнє оновлення:** 2026-08-22 17:55

---

## 📊 Рейтинг та завантаження

| Метрика | Значення | Джерело |
|---------|----------|---------|
| 📥 Встановлень (VS Code) | **74 421 021** | VS Code Marketplace API |
| ⭐ Рейтинг | **4.08 / 5** (1 054 оцінок) | VS Code Marketplace API |
| 📦 Версія | **1.388.0** (оновлено 2025-10-24) | VS Code Marketplace API |
| 🗓️ Дата публікації | 2021-06-29 | VS Code Marketplace API |
| 🏷️ Ліцензія | Proprietary (закритий код) | VS Code Marketplace |
| 💰 Ціна | **Trial** (платна підписка) | VS Code Marketplace |
| 📝 Опис | "Your AI pair programmer" | VS Code Marketplace API |
| 📦 Пакет | GitHub.copilot + GitHub.copilot-chat | VS Code Marketplace API |

> ⚠️ GitHub Copilot — закритий продукт, тому показників GitHub зірок/форків немає.

---

## 🔧 Опис функціоналу

**GitHub Copilot** — вбудований AI-асистент від GitHub (Microsoft), який з'явився одним із перших у 2021 році.

- ✅ **Inline-доповнення коду** — автодоповнення рядків і функцій під час набору
- ✅ **Чат (Copilot Chat)** — діалог з AI у VS Code, пояснення коду, рефакторинг
- ✅ **Пояснення коду** — "поясни що робить цей код"
- ✅ **Тести** — генерація юніт-тестів
- ✅ **Рефакторинг** — пропозиції покращення коду
- ✅ **Підтримка GitHub Copilot Workspace** — автономні задачі
- ✅ **Кросплатформенність** — VS Code, Visual Studio, JetBrains, Neovim, GitHub CLI
- ✅ **Інтеграція з GitHub** — PR-рев'ю, Copilot для pull requests
- ✅ **Підтримка правил** — через `.github/copilot-instructions.md` (файл інструкцій у репозиторії)

---

## 🎯 Переваги

- 👑 **Найбільша кількість встановлень** — понад 74 млн (найпопулярніший)
- 🎯 **Точне автодоповнення** — найкраще серед конкурентів для inline-комплітів
- 🔄 **Глибока інтеграція** — з GitHub, VS Code, всіма найпопулярнішими IDE
- 🛡️ **Підтримка корпоративних стандартів** — для бізнесу через GitHub Enterprise
- 🕐 **Швидкий** — модель працює на хмарі Microsoft
- 📚 **Якісна документація** та підтримка

---

## ⚠️ Недоліки

- 💸 **Платний** — потрібна підписка після пробного періоду
- 🔒 **Закритий код** — немає можливості самому налаштувати/доопрацювати
- 🎯 **Обмежений функціонал автономності** — Copilot не виконує сам команди так вільно, як Cline/OpenCode
- 🌐 **Менш гнучкий з локальними моделями** — прив'язаний до хмарних моделей GitHub
- 📅 **Пізніше оновлення** — остання версія 1.388.0 (жовтень 2025), хоча Marketplace показує 74 млн встановлень

---

## 🔗 Посилання

| Ресурс | URL |
|--------|-----|
| 🌐 Офіційний сайт | https://github.com/features/copilot |
| 📦 VS Code Marketplace | https://marketplace.visualstudio.com/items?itemName=GitHub.copilot |
| 📖 Документація | https://docs.github.com/copilot |
| 💬 Спільнота | https://github.com/github-community/community/discussions/categories/copilot |
| 📦 Copilot Chat | https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat |

---

## 🤝 Інтеграція з агентом Comfy-smart-lady

У проєкті GitHub Copilot використовує каталог **`.github/`** зі скриптами, з посиланнями або виконавчими файлами з посиланнями на канонічні файли:

- `.github/copilot-instructions.md` — інструкції для Copilot
- `.github/agents/Comfy-smart-lady.md` — канонічний файл агента - посилання на канонічний файл `AGENT\agents\Comfy-smart-lady.md`
- `.github/hooks/Loops.json` — anti-loop конфігурація
- `.github/memories_agent/` — внутрішні спогади агента (порожня папка, канонічна папка `AGENT\memories_agent`)
- `.github/scripts/agent_startup.py` — скрипт запуску скриптів агента
- `.github/state/vscode_agent_anti_loop_state.json` — стан anti-loop
- `.github/skills/`, `.github/knowledge-base/` — stub-посилання на канонічні `AGENT\skills` та `AGENT\knowledge-base`


---

*Цей файл — частина реєстру `AGENT/chats/`. Джерела даних: VS Code Marketplace API (2026-08-22).*