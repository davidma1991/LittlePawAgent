from typing import Any

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from app.config.loader import (
    load_agent_config, save_agent_config,
    load_mcp_servers, save_mcp_servers,
)
from app.llm.ollama import OllamaClient

router = APIRouter()


@router.get("/config")
async def get_config(request: Request) -> dict[str, Any]:
    """Get current agent configuration."""
    agent_config = load_agent_config()
    mcp_config = load_mcp_servers()

    # Include MCP server status if available
    mcp_manager = getattr(request.app.state, "mcp_manager", None)
    server_status = mcp_manager.get_server_status() if mcp_manager else {}

    return {
        "agent": agent_config,
        "mcp": mcp_config,
        "mcp_status": server_status,
    }


@router.put("/config")
async def update_config(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    """Update agent configuration."""
    agent_config = body.get("agent")
    mcp_config = body.get("mcp")

    if agent_config:
        save_agent_config(agent_config)
        # Update tool registry config
        tool_registry = getattr(request.app.state, "tool_registry", None)
        if tool_registry:
            tool_registry.update_config(agent_config)
        request.app.state.agent_config = agent_config

    if mcp_config:
        save_mcp_servers(mcp_config)

    return {"status": "ok"}


@router.get("/models")
async def list_models(request: Request) -> dict[str, Any]:
    """List available Ollama models."""
    agent_config = getattr(request.app.state, "agent_config", {})
    ollama_url = agent_config.get("ollama", {}).get("base_url", "http://localhost:11434")
    llm = OllamaClient(base_url=ollama_url)
    models = await llm.list_models()
    return {"models": models}


@router.get("/tools")
async def list_tools(request: Request) -> dict[str, Any]:
    """List all registered tools and their status."""
    tool_registry = getattr(request.app.state, "tool_registry", None)
    if not tool_registry:
        return {"tools": []}

    tools = []
    enabled_names = {t.name for t in tool_registry.list_enabled()}
    for tool in tool_registry.list_all():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "source": tool.source,
            "enabled": tool.name in enabled_names,
        })
    return {"tools": tools}
