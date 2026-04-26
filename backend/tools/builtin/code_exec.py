import asyncio
import sys
import tempfile
import os
from backend.tools.base import ToolDef


async def _run_python(code: str, timeout: int) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, tmp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
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
            return {"stdout": "", "stderr": f"Execution timed out after {timeout}s", "returncode": -1}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def make_code_exec_tool(timeout: int = 30) -> ToolDef:
    async def handler(code: str) -> dict:
        return await _run_python(code, timeout)

    return ToolDef(
        name="python_exec",
        description="Execute Python code and return stdout, stderr, and return code.",
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The Python code to execute"},
            },
            "required": ["code"],
        },
        handler=handler,
        source="builtin",
    )
