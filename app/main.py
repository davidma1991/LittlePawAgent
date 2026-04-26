from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

load_dotenv()

from app.api.chat import router as chat_router
from app.api.config import router as config_router
from app.tools.registry import ToolRegistry
from app.tools.mcp.client import MCPClientManager
from app.config.loader import load_agent_config, load_mcp_servers

FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_config = load_agent_config()
    mcp_config = load_mcp_servers()

    tool_registry = ToolRegistry(agent_config)
    tool_registry.register_builtins()

    mcp_manager = MCPClientManager(mcp_config, tool_registry)
    await mcp_manager.startup()

    app.state.tool_registry = tool_registry
    app.state.mcp_manager = mcp_manager
    app.state.agent_config = agent_config

    yield

    await mcp_manager.shutdown()


app = FastAPI(
    title="LittlePawAgent",
    description="A full-stack chat-based AI agent powered by local Ollama LLMs",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chat_router, prefix="/api")
app.include_router(config_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve built frontend — static files + SPA fallback
if FRONTEND_DIST.exists():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve static file if it exists, otherwise return index.html for SPA routing."""
        candidate = FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
