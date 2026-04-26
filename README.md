# LittlePaw Agent 🐾

A full-stack, chat-based AI agent powered by local Ollama LLMs. Supports tool calling (web search, code execution, bash, file ops, browser automation), MCP servers, and two execution modes (ReAct loop vs. Plan-then-Execute).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Ollama](https://ollama.ai) running locally
- Node.js 18+

## Quick Start

```bash
# 1. Install Python dependencies
uv sync

# 2. Build the frontend (once)
cd frontend && npm install && npm run build && cd ..

# 3. Pull a model (if not already done)
ollama pull llama3.2

# 4. Start the server — serves both API and UI
uv run uvicorn backend.main:app --reload
# → http://localhost:8000
```

Rebuild the frontend after UI changes: `cd frontend && npm run build`

## Optional Services

### SearXNG (web search)
```bash
docker run -d -p 8080:8080 searxng/searxng
```

### MCP Servers
Edit `config/mcp_servers.json` to enable/disable servers. The `filesystem` server (targeting `/tmp`) is enabled by default.

## Configuration

- `config/agent_config.json` — Ollama URL, model, tool settings
- `config/mcp_servers.json` — MCP server definitions

## Architecture

```
User ←SSE→ FastAPI ←→ Agent (ReAct / Plan-Execute)
                          ├── OllamaClient (httpx)
                          ├── ToolRegistry
                          │    ├── web_search (SearXNG)
                          │    ├── bash_exec
                          │    ├── python_exec
                          │    ├── read_file / write_file
                          │    ├── browser_use
                          │    └── mcp__* (from MCP servers)
                          └── MCPClientManager
```

## SSE Event Types

| Event | Description |
|-------|-------------|
| `thinking` | Agent reasoning text |
| `plan` | Plan-Execute step list |
| `plan_step_start/done` | Step lifecycle |
| `tool_start` | Tool invocation with input |
| `tool_result` | Tool output/error |
| `token` | Final answer token stream |
| `done` | Stream complete |
| `error` | Error message |
