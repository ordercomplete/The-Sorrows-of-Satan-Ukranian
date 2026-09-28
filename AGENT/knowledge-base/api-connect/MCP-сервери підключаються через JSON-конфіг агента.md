**Коротко:** MCP-сервери підключаються через JSON-конфіг агента (або CLI-команду). Нижче — практичні рецепти для Context7, GitHub, Tavily і Stack Overflow.

---

### 1. Де лежить конфіг (залежить від агента)

| Агент | Файл конфігу |
|-------|--------------|
| **Cursor** | `~/.cursor/mcp.json` (глобально) або `.cursor/mcp.json` (проект) |
| **Claude Code** | CLI: `claude mcp add ...` (або JSON) |
| **VS Code + Copilot** | `.vscode/mcp.json` або user settings (`mcp.servers`) |
| **Cline** | MCP Servers вкладка / `cline_mcp_settings.json` |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |

Формат майже скрізь однаковий: блок `mcpServers` з `command`+`args` (локальний stdio) або `url` (remote HTTP).

---

### 2. Context7 (документація бібліотек)

**Найшвидше:**
```bash
npx ctx7 setup
# або точково:
npx ctx7 setup --cursor
npx ctx7 setup --claude
```

**Вручну (Cursor / загальний JSON):**

Remote (рекомендовано):
```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Локально через npx:
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"]
    }
  }
}
```

**Claude Code:**
```bash
claude mcp add --scope user --header "CONTEXT7_API_KEY: YOUR_API_KEY" --transport http context7 https://mcp.context7.com/mcp
```

API-ключ (опційно, але бажано): [context7.com/dashboard](https://context7.com/dashboard). Без ключа теж працює, але з нижчими лімітами.

---

### 3. GitHub MCP (issues, PRs, code search)

Офіційний сервер: [github/github-mcp-server](https://github.com/github/github-mcp-server).  
Пакет `@modelcontextprotocol/server-github` **застарілий** — не використовуй його.

**Remote (найпростіше, VS Code / Copilot):**
```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```
(у VS Code часто використовується ключ `servers`, не `mcpServers`)

**З PAT (Personal Access Token):**
```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_GITHUB_PAT"
      }
    }
  }
}
```

**Claude Code (remote + PAT):**
```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp/","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
```

**Локально через Docker** (потрібен Docker):
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
      }
    }
  }
}
```

PAT: [GitHub → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens). Мінімум scopes: `repo`, `read:org` (залежно від задач).

---

### 4. Tavily (веб-пошук)

Потрібен API-ключ: [app.tavily.com](https://app.tavily.com/home) (є безкоштовний tier).

**Локально (Cursor / Cline / Claude Desktop):**
```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "tvly-YOUR_API_KEY"
      }
    }
  }
}
```

**Remote (Claude Code):**
```bash
claude mcp add --transport http tavily "https://mcp.tavily.com/mcp/?tavilyApiKey=tvly-YOUR_API_KEY"
```

**Cline:** часто можна встановити одним кліком з MCP marketplace (вкладка MCP Servers → пошу Tavily → Install), потім вставити ключ.

---

### 5. Stack Overflow

**Варіант A — community (`@gscalzo/stackoverflow-mcp`):**
```json
{
  "mcpServers": {
    "stackoverflow": {
      "command": "npx",
      "args": ["-y", "@gscalzo/stackoverflow-mcp"],
      "env": {
        "STACKOVERFLOW_API_KEY": "optional-key"
      }
    }
  }
}
```
Ключ опційний (підвищує rate limit): [stackapps.com](https://stackapps.com/).

**Варіант B — офіційний remote (OAuth):**
```json
{
  "mcpServers": {
    "stackoverflow": {
      "command": "npx",
      "args": ["mcp-remote", "mcp.stackoverflow.com"]
    }
  }
}
```
Після першого запуску клієнт відкриє логін Stack Exchange.

---

### 6. Готовий мінімальний стек (один файл для Cursor)

`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_CONTEXT7_KEY"
      }
    },
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_GITHUB_PAT"
      }
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "tvly-YOUR_KEY"
      }
    },
    "stackoverflow": {
      "command": "npx",
      "args": ["-y", "@gscalzo/stackoverflow-mcp"]
    }
  }
}
```

Після збереження — **перезапусти** агент/IDE.

---

### 7. Перевірка, що все працює

1. У Cursor: Settings → MCP — сервери мають бути зеленими / connected.
2. У Claude Code: `claude mcp list` або команда `/mcp`.
3. У чаті агента (Agent mode):  
   - «Знайди через Context7 docs для React 19 useEffect»  
   - «Пошукай на Stack Overflow помилку …»  
   - «Знайди issues у vercel/next.js про …»

Якщо інструмент не з’являється — перевір, що увімкнено **Agent mode** (не звичайний Ask), і що JSON валідний (коми, лапки).

---

### Важливі нюанси

- **Ключі не коміть у git.** Глобальний `~/.cursor/mcp.json` безпечніший за `.cursor/mcp.json` у репо.
- На **Windows** інколи потрібен обгортка: `"command": "cmd", "args": ["/c", "npx", "-y", "..."]`.
- Завжди став `-y` після `npx`, інакше сервер може «зависнути» на підтвердженні встановлення.
- Потрібен **Node.js** (краще ≥ 20) для `npx`-серверів.

Якщо скажеш, який саме агент використовуєш (Cursor / Cline / Copilot / Claude Code), можу дати один точний файл конфігу під нього без зайвих варіантів.