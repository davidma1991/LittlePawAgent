from pathlib import Path
from backend.tools.base import ToolDef


def _is_allowed_path(file_path: str, allowed_paths: list[str]) -> bool:
    abs_path = Path(file_path).resolve()
    for allowed in allowed_paths:
        try:
            abs_path.relative_to(Path(allowed).resolve())
            return True
        except ValueError:
            continue
    return False


def make_file_read_tool(allowed_paths: list[str]) -> ToolDef:
    async def handler(file_path: str) -> str:
        if not _is_allowed_path(file_path, allowed_paths):
            raise PermissionError(f"Access denied: {file_path} is not in allowed paths {allowed_paths}")
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path.read_text(encoding="utf-8")

    return ToolDef(
        name="read_file",
        description="Read the contents of a file. Only files in allowed directories can be read.",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The absolute path to the file to read"},
            },
            "required": ["file_path"],
        },
        handler=handler,
        source="builtin",
    )


def make_file_write_tool(allowed_paths: list[str]) -> ToolDef:
    async def handler(file_path: str, content: str) -> str:
        if not _is_allowed_path(file_path, allowed_paths):
            raise PermissionError(f"Access denied: {file_path} is not in allowed paths {allowed_paths}")
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to {file_path}"

    return ToolDef(
        name="write_file",
        description="Write content to a file. Only files in allowed directories can be written.",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The absolute path to the file to write"},
                "content": {"type": "string", "description": "The content to write to the file"},
            },
            "required": ["file_path", "content"],
        },
        handler=handler,
        source="builtin",
    )
