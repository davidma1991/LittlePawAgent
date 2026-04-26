from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class ToolDef:
    """Definition of a tool that can be called by the agent."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema object
    handler: Callable[..., Awaitable[Any]]
    enabled: bool = True
    source: str = "builtin"  # "builtin" | "mcp"

    def to_openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class ToolResult:
    """Result of a tool execution."""
    tool_name: str
    call_id: str
    output: Any = None
    error: str | None = None
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "call_id": self.call_id,
            "output": self.output,
            "error": self.error,
            "success": self.success,
        }
