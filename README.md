# LittlePaw Agent 🐾

A full-stack, chat-based AI agent powered by **local Ollama LLMs**. No cloud API keys required — everything runs on your machine.

## Features

- **Two agent modes** — ReAct loop (fast, iterative) and Plan-then-Execute (structured, multi-step)
- **Built-in tools** — web search, Python execution, bash, file read/write, browser automation
- **MCP support** — connect any [Model Context Protocol](https://modelcontextprotocol.io) server via stdio or HTTP
- **Live tool visibility** — collapsible panels show every tool call input/output in real time
- **SSE streaming** — tokens, tool events, and plan steps stream as they happen
- **Single server** — FastAPI serves both the API and the built React frontend

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, `uv` |
| LLM | Ollama (OpenAI-compatible `/v1` API) |
| Browser automation | `browser-use` |
| MCP | `mcp` Python SDK (stdio + HTTP) |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS |
| Streaming | Server-Sent Events (SSE) |

## Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- [Ollama](https://ollama.ai) — running locally with at least one model pulled
- [Node.js 18+](https://nodejs.org) — for building the frontend

## Quick Start

```bash
# 1. Install Python dependencies
uv sync

# 2. Build the frontend
cd frontend && npm install && npm run build && cd ..

# 3. Pull an Ollama model (if not already done)
ollama pull qwen2.5:72b

# 4. Start the server
uv run uvicorn backend.main:app --reload
```

Open **http://localhost:8000** in your browser.

> After making UI changes, rebuild with: `cd frontend && npm run build`

## Optional Services

### Web Search — SearXNG

The `web_search` tool requires a local [SearXNG](https://searxng.github.io/searxng/) instance. It is **disabled by default** — enable it after starting SearXNG:

```bash
docker run -d -p 8080:8080 searxng/searxng
```

Then in `config/agent_config.json` set:
```json
"web_search": { "enabled": true, "searxng_url": "http://localhost:8080" }
```

### MCP Servers

Edit `config/mcp_servers.json` to enable servers. The `filesystem` server (targeting `/tmp`) is enabled by default. Example:

```json
{
  "mcpServers": {
    "filesystem": {
      "enabled": true,
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

Enabled MCP servers connect on startup and their tools appear automatically in the sidebar.

## Configuration

### `config/agent_config.json`

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "default_model": "llama3.2"
  },
  "tools": {
    "web_search": { "enabled": true, "searxng_url": "http://localhost:8080" },
    "file_ops":   { "enabled": true, "allowed_paths": ["/tmp"] },
    "code_exec":  { "enabled": true, "timeout": 30 },
    "bash":       { "enabled": true, "timeout": 30 },
    "browser":    { "enabled": true, "headless": true }
  }
}
```

### `config/mcp_servers.json`

Defines MCP server connections. Supports `stdio` (local process) and `http` transports.

## Project Structure

```
LittlePawAgent/
├── backend/
│   ├── main.py                  # FastAPI app, serves API + built frontend
│   ├── api/
│   │   ├── chat.py              # POST /api/chat/stream  (SSE)
│   │   └── config.py            # GET/PUT /api/config, GET /api/models, /api/tools
│   ├── agent/
│   │   ├── base.py              # BaseAgent + StreamEvent dataclasses
│   │   ├── react.py             # ReAct loop agent
│   │   ├── plan_execute.py      # Plan-then-Execute agent
│   │   └── prompts.py           # System prompts
│   ├── tools/
│   │   ├── registry.py          # ToolRegistry (register, list, execute)
│   │   ├── builtin/             # web_search, file_ops, code_exec, bash, browser
│   │   └── mcp/                 # MCP client manager + adapter
│   ├── llm/
│   │   └── ollama.py            # Async Ollama client (streaming, tool calls)
│   └── config/
│       └── loader.py            # Load/save config JSON files
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Chat/            # ChatWindow, MessageList, MessageBubble, MessageInput
│       │   ├── Agent/           # ThinkingCard, PlanCard, ToolCallCard
│       │   └── Sidebar/         # ModelSelector, PlanModeToggle, ToolList, McpServerList
│       ├── hooks/
│       │   ├── useChat.ts       # SSE stream → message state
│       │   └── useConfig.ts     # Config, models, and tools state
│       └── lib/
│           └── api.ts           # Fetch wrappers + SSE client
├── config/
│   ├── agent_config.json
│   └── mcp_servers.json
└── pyproject.toml
```

## Agent Modes

### ReAct (default)

Iterative Reason → Act → Observe loop. The agent calls tools one at a time, observes the result, and decides whether to call another tool or produce a final answer.

```
user message → [think] → tool call → [observe] → tool call → ... → final answer
```

### Plan-Execute

Better for complex, multi-step tasks. The agent first generates a structured plan, executes each step with its own mini ReAct loop, then synthesizes a final answer from all results.

```
user message → [plan] → step 1 → step 2 → step 3 → [synthesize] → final answer
```

## SSE Event Schema

All agent actions stream as JSON events over SSE:

| Event | Fields | Description |
|---|---|---|
| `thinking` | `content` | Agent reasoning text |
| `plan` | `steps[]` | Plan-Execute step list with status |
| `plan_step_start` | `step_id` | Step begins executing |
| `plan_step_done` | `step_id`, `summary` | Step completed |
| `tool_start` | `call_id`, `tool`, `input` | Tool invocation |
| `tool_result` | `call_id`, `tool`, `output`, `error` | Tool result |
| `token` | `content` | Final answer token |
| `done` | — | Stream complete |
| `error` | `message` | Error occurred |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/chat/stream` | Stream agent response (SSE) |
| `GET` | `/api/config` | Get agent + MCP config |
| `PUT` | `/api/config` | Update config |
| `GET` | `/api/models` | List available Ollama models |
| `GET` | `/api/tools` | List registered tools |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | FastAPI interactive docs |

## License

MIT
