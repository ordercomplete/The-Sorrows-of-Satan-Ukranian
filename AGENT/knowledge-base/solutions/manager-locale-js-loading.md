# Як ComfyUI завантажує JS від кастомних нод

## Механізм завантаження JavaScript

### Backend Flow (Python Custom Nodes):
1. ComfyUI server запускається → сканує `/custom_nodes/` директорії
2. Завантажує Python модулі (наприклад, `/custom_nodes/ComfyUI-Impact-Pack/__init__.py`)
3. Python код реєструє нові типи нод з сервером
4. Сервер експонує їх через `/object_info` API з метаданими типу `python_module: "custom_nodes.ComfyUI-Impact-Pack"`
5. Ноди виконуються на сервері при запуску workflow

### Frontend Flow (JavaScript):

**Core Extensions (вбудовані):**
1. Вбудовані безпосередньо у фронтенд bundle в `/src/extensions/core/`
2. Завантажуються одразу при старті фронтенду
3. Не потрібні мережеві запити — частина зібраного коду

**Custom Node JavaScript (динамічне завантаження):**
1. Frontend запускається → викликає `/extensions` API
2. Server повертає список JS файлів з:
   - `/web/extensions/*.js` (застаріле місце)
   - `/custom_nodes/*/web/*.js` (node-specific UI код)
3. Frontend завантажує кожен JS файл (fetch)
4. JS виконується одразу, викликає `app.registerExtension()` для хуку в UI
5. Зареєстровані хуки покращують UI для відповідних Python нод

### Ключова відмінність:
- **Python nodes** = Backend обробка (що показується в меню нод)
- **JavaScript extensions** = Frontend покращення (як ноди виглядають/поведінка в UI)
- Custom node пакет може мати обидва, тільки Python, або (рідко) тільки JavaScript

## WEB_DIRECTORY

### Як реєструється:
```python
# В __init__.py кастомної ноди
WEB_DIRECTORY = "js"  # або "web"
```

### Як працює:
1. ComfyUI сканує `__init__.py` кожної ноди
2. Якщо знаходить `WEB_DIRECTORY` — додає шлях до `nodes.EXTENSION_WEB_DIRS`
3. Під час запуску сервер додає статичні файли:
   ```python
   for name, dir in nodes.EXTENSION_WEB_DIRS.items():
       self.app.add_routes([web.static('/extensions/' + name, dir)])
   ```
4. `/extensions` API повертає список всіх JS URL

### Реєстрація через EXTENSION_WEB_DIRS:
```python
# В prestartup_script.py або __init__.py
import nodes
nodes.EXTENSION_WEB_DIRS["my-extension"] = os.path.join(os.path.dirname(__file__), "web")
```

## app.registerExtension()

### Як працює:
```javascript
app.registerExtension({
    name: "My.Extension.Name",
    aboutPageBadges: [...],
    commands: [...],
    init() { /* викликається при реєстрації */ },
    setup() { /* викликається перед setup app */ },
    ready() { /* викликається після setup app */ }
});
```

### Приклад з ComfyUI Manager:
```javascript
app.registerExtension({
    name: "Comfy.ManagerMenu",
    aboutPageBadges: [
        {
            label: `ComfyUI-Manager ${manager_version}`,
            url: 'https://github.com/ltdrdata/ComfyUI-Manager',
            icon: 'pi pi-th-large'
        }
    ],
    commands: [
        {
            id: "Com.Manager.Menu.ToggleVisibility",
            label: "Toggle Manager Menu Visibility",
            icon: "mdi mdi-puzzle",
            function: () => { /* ... */ }
        }
    ],
    init() { /* ... */ }
});
```

## prestartup_script.py

### Коли виконується:
- **Тільки при запуску ComfyUI сервера**
- Не виконується при перезавантаженні браузера!

### Як знаходить скрипти:
```python
# В main.py
def execute_prestartup_script():
    node_paths = folder_paths.get_folder_paths("custom_nodes")
    for custom_node_path in node_paths:
        possible_modules = os.listdir(custom_node_path)
        for possible_module in possible_modules:
            module_path = os.path.join(custom_node_path, possible_module)
            script_path = os.path.join(module_path, "prestartup_script.py")
            if os.path.exists(script_path):
                execute_script(script_path)
```

### Важливо:
- `prestartup_script.py` виконується **тільки при запуску ComfyUI**
- Якщо створити новий файл після запуску — потрібно **перезапустити ComfyUI**
- Скрипт шукається в кожній папці `custom_nodes/*/prestartup_script.py`

## Джерела:
- https://docs.comfy.org/custom-nodes/overview
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/development.md
- https://docs.comfy.org/custom-nodes/backend/lifecycle#web-directory
