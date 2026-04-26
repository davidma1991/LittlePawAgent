from typing import Any
from app.tools.base import ToolDef


def mcp_tool_to_tooldef(server_name: str, mcp_tool, session) -> ToolDef:
    tool_name = f"mcp__{server_name}__{mcp_tool.name}"
    parameters = mcp_tool.inputSchema or {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def handler(**kwargs: Any) -> Any:
        result = await session.call_tool(mcp_tool.name, arguments=kwargs)
        if result.content:
            texts = []
            for item in result.content:
                if hasattr(item, "text"):
                    texts.append(item.text)
                else:
                    texts.append(str(item))
            return "\n".join(texts)
        return "Tool executed successfully (no output)"

    return ToolDef(
        name=tool_name,
        description=mcp_tool.description or f"MCP tool from server '{server_name}'",
        parameters=parameters,
        handler=handler,
        enabled=True,
        source="mcp",
    )
