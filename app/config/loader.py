import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path(__file__).parent
AGENT_CONFIG_PATH = CONFIG_DIR / "agent_config.json"
MCP_SERVERS_PATH = CONFIG_DIR / "mcp_servers.json"


def load_agent_config() -> dict[str, Any]:
    """Load agent configuration from agent_config.json."""
    if not AGENT_CONFIG_PATH.exists():
        return _default_agent_config()
    with open(AGENT_CONFIG_PATH) as f:
        return json.load(f)


def save_agent_config(config: dict[str, Any]) -> None:
    """Save agent configuration to agent_config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(AGENT_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def load_mcp_servers() -> dict[str, Any]:
    """Load MCP server definitions from mcp_servers.json."""
    if not MCP_SERVERS_PATH.exists():
        return {"mcpServers": {}}
    with open(MCP_SERVERS_PATH) as f:
        return json.load(f)


def save_mcp_servers(config: dict[str, Any]) -> None:
    """Save MCP server definitions to mcp_servers.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(MCP_SERVERS_PATH, "w") as f:
        json.dump(config, f, indent=2)


def _default_agent_config() -> dict[str, Any]:
    return {
        "ollama": {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "default_model": os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2"),
        },
        "tools": {
            "web_search": {"enabled": True, "searxng_url": "http://localhost:8080"},
            "file_ops": {"enabled": True, "allowed_paths": ["/tmp"]},
            "code_exec": {"enabled": True, "timeout": 30},
            "bash": {"enabled": True, "timeout": 30, "allowed_commands": []},
            "browser": {"enabled": True, "headless": True},
        },
    }
