import asyncio
import os
from backend.tools.base import ToolDef


async def _run_bash(command: str, timeout: int) -> dict:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=os.environ.copy(),
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "returncode": proc.returncode,
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"stdout": "", "stderr": f"Command timed out after {timeout}s", "returncode": -1}


def make_bash_tool(timeout: int = 30) -> ToolDef:
    async def handler(command: str) -> dict:
        return await _run_bash(command, timeout)

    return ToolDef(
        name="bash_exec",
        description="Execute a bash command and return stdout, stderr, and return code.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The bash command to execute"},
            },
            "required": ["command"],
        },
        handler=handler,
        source="builtin",
    )
