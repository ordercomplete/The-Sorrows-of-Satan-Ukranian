Ось **точні інструкції** під твій стек: **Cline**, **GitHub Copilot (VS Code)** і **LM Studio Code**.

---

## 1. Cline (VS Code extension)

### Як відкрити конфіг
1. Відкрий панель **Cline**
2. Іконка **MCP Servers** (зверху)
3. Вкладка **Configure** → **Configure MCP Servers**

Це відкриє `cline_mcp_settings.json`.

**Шляхи файлу:**
| ОС | Шлях |
|----|------|
| Linux | `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` |
| macOS | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` |
| Windows | `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json` |

### Готовий конфіг для Cline

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {
        "CONTEXT7_API_KEY": "YOUR_CONTEXT7_KEY"
      },
      "disabled": false,
      "autoApprove": []
    },
    "github": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.githubcopilot.com/mcp/"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
      },
      "disabled": false,
      "autoApprove": []
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "tvly-YOUR_KEY"
      },
      "disabled": false,
      "autoApprove": []
    },
    "stackoverflow": {
      "command": "npx",
      "args": ["-y", "@gscalzo/stackoverflow-mcp"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Альтернатива для **Context7 remote** (без локального процесу):

```json
"context7": {
  "url": "https://mcp.context7.com/mcp",
  "headers": {
    "CONTEXT7_API_KEY": "YOUR_CONTEXT7_KEY"
  },
  "disabled": false
}
```

**Cline Marketplace:** Tavily часто можна поставити в 1 клік (MCP Servers → пошу «Tavily» → Install), потім лише вставити ключ.

Після збереження — Reload Window або новий чат Cline.

---

## 2. GitHub Copilot (VS Code)

**Важливо:** у VS Code ключ верхнього рівня — **`servers`**, не `mcpServers`.

### Варіанти розміщення
| Місце | Коли |
|-------|------|
| `.vscode/mcp.json` у проєкті | для команди / репо |
| User config | Command Palette → **MCP: Open User Configuration** (для всіх проєктів) |

### Готовий `.vscode/mcp.json`

```json
{
  "inputs": [
    {
      "id": "context7_key",
      "type": "promptString",
      "description": "Context7 API Key",
      "password": true
    },
    {
      "id": "tavily_key",
      "type": "promptString",
      "description": "Tavily API Key",
      "password": true
    },
    {
      "id": "github_token",
      "type": "promptString",
      "description": "GitHub PAT",
      "password": true
    }
  ],
  "servers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${input:context7_key}"
      }
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "${input:tavily_key}"
      }
    },
    "stackoverflow": {
      "command": "npx",
      "args": ["-y", "@gscalzo/stackoverflow-mcp"]
    }
  }
}
```

### Як увімкнути
1. Збережи файл → з’явиться кнопка **Start** над серверами
2. Натисни **Start** (для GitHub часто OAuth через акаунт GitHub)
3. У Chat перемкни режим на **Agent** (не Ask)
4. Інструменти з’являться в tools picker / через `#`

Швидке додавання: `Ctrl+Shift+P` → **MCP: Add Server**.

---

## 3. LM Studio Code (VS Code extension)

LM Studio Code **підхоплює MCP з кількох місць** (пріоритет зверху вниз):

1. `.mcp.json` у корені проєкту (`mcpServers`)
2. `.vscode/mcp.json` (`servers`) — той самий, що для Copilot
3. User-level MCP VS Code
4. Налаштування `lmstudioCode.mcpServers`

Тобто **якщо вже налаштував Copilot через `.vscode/mcp.json` — LM Studio Code теж їх побачить**.

### Окремо тільки для LM Studio Code

У VS Code Settings (`settings.json`):

```json
"lmstudioCode.mcpServers": {
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"],
    "env": {
      "CONTEXT7_API_KEY": "YOUR_CONTEXT7_KEY"
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
```

### Якщо використовуєш LM Studio app (не лише extension)

1. У LM Studio → вкладка **Program** (права панель)
2. **Install → Edit mcp.json**
3. Формат як у Cursor:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_CONTEXT7_KEY"
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

**Увага:** локальні моделі гірше справляються з великою кількістю tools. Почни з 2–3 серверів (Context7 + Tavily), інакше швидко заповнюється context.

---

## Практична схема «один раз — для всіх трьох»

Найменше дублювання:

| Файл | Хто читає |
|------|-----------|
| `.vscode/mcp.json` | **Copilot** + **LM Studio Code** |
| `cline_mcp_settings.json` | **тільки Cline** (окремий файл) |

Скопіюй ті самі 4 сервери в обидва місця з правильним ключем верхнього рівня:
- Cline → `mcpServers`
- VS Code / Copilot → `servers`

---

## Ключі, які потрібні

| Сервіс | Де взяти | Обов’язково? |
|--------|----------|--------------|
| **Context7** | [context7.com/dashboard](https://context7.com/dashboard) | Ні, але бажано |
| **Tavily** | [app.tavily.com](https://app.tavily.com/home) | Так |
| **GitHub** | PAT або OAuth у Copilot | Так для приватних репо |
| **Stack Overflow** | без ключа ОК; опційно Stack Apps | Ні |

---

## Швидка перевірка

У чаті кожного агента:

1. «Use Context7 to get the docs for `express` router»
2. «Search Stack Overflow for: Cannot read properties of undefined reading map»
3. «Search the web with Tavily: Next.js 15 metadata API»

Якщо tool call не з’являється — сервер не стартував або не Agent mode.

Можу зібрати **один мінімальний набір** (лише Context7 + Tavily) під Cline і окремо під `.vscode/mcp.json`, якщо хочеш почати без GitHub/SO.