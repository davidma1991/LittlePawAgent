import json
from typing import Any, AsyncIterator

import httpx


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.v1_url = f"{self.base_url}/v1"

    async def list_models(self) -> list[str]:
        """List available models from Ollama."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
            except Exception:
                return []

    async def chat(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Non-streaming chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.v1_url}/chat/completions",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream tokens from chat completion. Yields token strings."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.v1_url}/chat/completions",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta and delta["content"]:
                            yield delta["content"]
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    def parse_tool_calls(self, response: dict) -> list[dict] | None:
        """Extract tool calls from a chat completion response."""
        try:
            message = response["choices"][0]["message"]
            tool_calls = message.get("tool_calls")
            if not tool_calls:
                return None
            result = []
            for tc in tool_calls:
                func = tc.get("function", {})
                args = func.get("arguments", "{}")
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                result.append({
                    "id": tc.get("id", ""),
                    "name": func.get("name", ""),
                    "arguments": args,
                })
            return result if result else None
        except (KeyError, IndexError):
            return None

    def get_content(self, response: dict) -> str:
        """Extract text content from a chat completion response."""
        try:
            return response["choices"][0]["message"].get("content") or ""
        except (KeyError, IndexError):
            return ""
