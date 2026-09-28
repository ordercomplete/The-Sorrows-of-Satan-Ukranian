# Універсальний механізм: розділення файлів проєкту та файлів Агента

## Призначення

Цей документ — елемент бази знань Агента (`AGENT/knowledge-base/plans-for-future/`). Він описує **універсальний механізм**, який дозволяє в будь-якому проєкті, де встановлено Агента Comfy-smart-lady, розділити файли на:

- **файли Агента** — керуються через `agent_config/manifest.json`, синхронізуються у репозиторій Агента `Comfy-smart-lady-agent.git` (гілка `main`);
- **файли проєкту** — все інше, що належить конкретному проєкту, збирається у теку `Files_project/` та пушиться у репозиторій проєкту (для Music Doc: `Music_Doc.git`, гілка `main`).

## Система визначення файлів Агента

Агент визначає власні файли через `agent_config/manifest.json`:

- `files` — канонічні джерела в `AGENT/` (16 записів);
- `root_files` — файли, що копіюються в корінь проєкту;
- `stub_files` — стаб-копії для різних чатів.

Разом маніфест задає 453 цільові шляхи (для версії 1.4.0). Усі ці файли належать Агенту. Ця система працює однаково в будь-якому проєкті.

## Файли проєкту

Файли проєкту — це все, що не входить у структуру, визначену маніфестом. Для спрощення розділення вони зберігаються в окремій теці `Files_project/`.

### Поточний склад `Files_project/`

1. `Процес обробки треку.md`
2. `Ultimate Vocal Remover (UVR5) — повний огляд.md`
3. `Install_Comfy-smart-lady-agent.txt`

## Кроки (алгоритм дій)

### Крок 1. Визначити файли проєкту

Прочитати `agent_config/manifest.json` та виокремити файли, яких у маніфесті немає. Саме вони є файлами проєкту.

### Крок 2. Перенести файли проєкту у теку `Files_project/`

```
Files_project/
├── Процес обробки треку.md
├── Ultimate Vocal Remover (UVR5) — повний огляд.md
└── Install_Comfy-smart-lady-agent.txt
```

### Крок 3. Створити гілку `project` без історії

```bash
git switch --orphan project
git rm -r --cached .
```

### Крок 4. Додати проєктні файли в індекс

```bash
git add Files_project/
```

### Крок 5. Створити проєктний `.gitignore`

Створити файл `.gitignore` у корені (у гілці `project`), щоб ігнорувати всі файли Агента:

```
AGENT/
agent_config/
.github/
.clinerules/
.continue/
.opencode/
.vscode/
trash/
agent-lock.json
reinstall_log.md
```

### Крок 6. Зафіксувати зміни та повернутись на `main`

```bash
git add -A
git commit -m "feat: файли проєкту (Files_project)"
git switch main
```

### Крок 7. Додати окремий remote для проєкту

```bash
git remote add origin-music https://github.com/ordercomplete/Music_Doc.git
```

### Крок 8. Запушити кожну гілку у свій репозиторій

```bash
git push origin main                       # Агент → Comfy-smart-lady-agent.git
git push origin-music project:main         # Проєкт → Music_Doc.git
```

## Перевірка результату

- `git status` — робоча директорія чиста;
- у `Music_Doc.git` будуть лише файли проєкту (тека `Files_project/`) та `.gitignore`;
- у `Comfy-smart-lady-agent.git` — лише файли Агента.

## Примітки та універсальність

- Файли Агента залишаються на диску; вони лише ігноруються у гілці `project`.
- Кроки 5–6 змінюють стан індексу та робочої директорії.
- Для іншого проєкту достатньо змінити: URL репозиторію у кроці 7 та вміст теки `Files_project/`.
- Механізм працює незалежно від того, які саме файли Агента використовує проєкт, оскільки «системою правди» завжди є `agent_config/manifest.json`.