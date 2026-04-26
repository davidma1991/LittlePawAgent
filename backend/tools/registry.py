import uuid
from typing import Any

from backend.tools.base import ToolDef, ToolResult


class ToolRegistry:
    def __init__(self, agent_config: dict[str, Any]):
        self._tools: dict[str, ToolDef] = {}
        self._config = agent_config

    def register(self, tool_def: ToolDef) -> None:
        self._tools[tool_def.name] = tool_def

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> ToolDef | None:
        return self._tools.get(name)

    def list_all(self) -> list[ToolDef]:
        return list(self._tools.values())

    # Maps tool.name → config key in agent_config.json tools section
    _TOOL_CONFIG_KEY: dict[str, str] = {
        "web_search": "web_search",
        "read_file": "file_ops",
        "write_file": "file_ops",
        "python_exec": "code_exec",
        "bash_exec": "bash",
        "browser_use": "browser",
    }

    def list_enabled(self) -> list[ToolDef]:
        tools_config = self._config.get("tools", {})
        result = []
        for tool in self._tools.values():
            if tool.source == "builtin":
                config_key = self._TOOL_CONFIG_KEY.get(tool.name, tool.name)
                tool_cfg = tools_config.get(config_key, {})
                if tool_cfg.get("enabled", tool.enabled):
                    result.append(tool)
            elif tool.source == "mcp":
                if tool.enabled:
                    result.append(tool)
        return result

    def to_openai_schema(self) -> list[dict[str, Any]]:
        return [t.to_openai_schema() for t in self.list_enabled()]

    async def execute(self, name: str, input_dict: dict[str, Any], call_id: str | None = None) -> ToolResult:
        if call_id is None:
            call_id = str(uuid.uuid4())[:8]
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(
                tool_name=name,
                call_id=call_id,
                error=f"Tool '{name}' not found",
                success=False,
            )
        try:
            output = await tool.handler(**input_dict)
            return ToolResult(
                tool_name=name,
                call_id=call_id,
                output=output,
                success=True,
            )
        except Exception as e:
            return ToolResult(
                tool_name=name,
                call_id=call_id,
                error=str(e),
                success=False,
            )

    def register_builtins(self) -> None:
        from backend.tools.builtin.web_search import make_web_search_tool
        from backend.tools.builtin.file_ops import make_file_read_tool, make_file_write_tool
        from backend.tools.builtin.code_exec import make_code_exec_tool
        from backend.tools.builtin.bash import make_bash_tool
        from backend.tools.builtin.browser_tool import make_browser_tool

        tools_config = self._config.get("tools", {})
        ollama_config = self._config.get("ollama", {})

        ws_cfg = tools_config.get("web_search", {})
        self.register(make_web_search_tool(ws_cfg.get("searxng_url", "http://localhost:8080")))

        fo_cfg = tools_config.get("file_ops", {})
        self.register(make_file_read_tool(fo_cfg.get("allowed_paths", ["/tmp"])))
        self.register(make_file_write_tool(fo_cfg.get("allowed_paths", ["/tmp"])))

        ce_cfg = tools_config.get("code_exec", {})
        self.register(make_code_exec_tool(ce_cfg.get("timeout", 30)))

        bash_cfg = tools_config.get("bash", {})
        self.register(make_bash_tool(bash_cfg.get("timeout", 30)))

        browser_cfg = tools_config.get("browser", {})
        ollama_url = ollama_config.get("base_url", "http://localhost:11434")
        ollama_model = ollama_config.get("default_model", "llama3.2")
        self.register(make_browser_tool(
            headless=browser_cfg.get("headless", True),
            ollama_base_url=ollama_url,
            ollama_model=ollama_model,
        ))

    def update_config(self, new_config: dict[str, Any]) -> None:
        self._config = new_config
