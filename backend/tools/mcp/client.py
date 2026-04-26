import logging
from typing import Any

logger = logging.getLogger(__name__)


class MCPClientManager:
    def __init__(self, mcp_config: dict[str, Any], tool_registry):
        self._config = mcp_config
        self._registry = tool_registry
        self._sessions: dict[str, Any] = {}
        self._server_status: dict[str, str] = {}
        self._context_managers: list[Any] = []

    async def startup(self) -> None:
        servers = self._config.get("mcpServers", {})
        for name, server_cfg in servers.items():
            if not server_cfg.get("enabled", False):
                self._server_status[name] = "disabled"
                continue
            try:
                await self._connect_server(name, server_cfg)
                self._server_status[name] = "connected"
                logger.info(f"MCP server '{name}' connected")
            except Exception as e:
                self._server_status[name] = f"error: {str(e)}"
                logger.warning(f"Failed to connect MCP server '{name}': {e}")

    async def _connect_server(self, name: str, cfg: dict[str, Any]) -> None:
        transport = cfg.get("transport", "stdio")
        if transport == "stdio":
            await self._connect_stdio(name, cfg)
        elif transport == "http":
            await self._connect_http(name, cfg)
        else:
            raise ValueError(f"Unknown transport: {transport}")

    async def _connect_stdio(self, name: str, cfg: dict[str, Any]) -> None:
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            command = cfg.get("command", "")
            args = cfg.get("args", [])
            server_params = StdioServerParameters(command=command, args=args)

            cm = stdio_client(server_params)
            read, write = await cm.__aenter__()
            self._context_managers.append(cm)

            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()

            self._sessions[name] = session
            await self._register_server_tools(name, session)
        except Exception as e:
            raise RuntimeError(f"Failed to connect stdio MCP server '{name}': {e}") from e

    async def _connect_http(self, name: str, cfg: dict[str, Any]) -> None:
        try:
            from mcp import ClientSession
            from mcp.client.sse import sse_client

            url = cfg.get("url", "")
            cm = sse_client(url)
            read, write = await cm.__aenter__()
            self._context_managers.append(cm)

            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()

            self._sessions[name] = session
            await self._register_server_tools(name, session)
        except Exception as e:
            raise RuntimeError(f"Failed to connect HTTP MCP server '{name}': {e}") from e

    async def _register_server_tools(self, name: str, session) -> None:
        from backend.tools.mcp.adapter import mcp_tool_to_tooldef
        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            tool_def = mcp_tool_to_tooldef(name, tool, session)
            self._registry.register(tool_def)
            logger.info(f"Registered MCP tool: {tool_def.name}")

    async def shutdown(self) -> None:
        for name, session in self._sessions.items():
            try:
                await session.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing MCP session '{name}': {e}")
        for cm in self._context_managers:
            try:
                await cm.__aexit__(None, None, None)
            except Exception:
                pass
        self._sessions.clear()
        self._context_managers.clear()

    def get_server_status(self) -> dict[str, str]:
        return dict(self._server_status)
