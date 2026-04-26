import json
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from backend.agent.react import ReActAgent
from backend.agent.plan_execute import PlanExecuteAgent
from backend.llm.ollama import OllamaClient

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2"
    mode: str = "react"  # "react" | "plan_execute"
    conversation_history: list[dict] = []


@router.post("/chat/stream")
async def chat_stream(request: Request, body: ChatRequest):
    """SSE endpoint for streaming agent responses."""
    app = request.app
    tool_registry = app.state.tool_registry
    agent_config = app.state.agent_config

    ollama_config = agent_config.get("ollama", {})
    ollama_url = ollama_config.get("base_url", "http://localhost:11434")

    llm = OllamaClient(base_url=ollama_url)

    if body.mode == "plan_execute":
        agent = PlanExecuteAgent(llm, tool_registry, body.model, agent_config)
    else:
        agent = ReActAgent(llm, tool_registry, body.model, agent_config)

    async def event_generator():
        try:
            async for event in agent.run(body.message, body.conversation_history):
                yield {
                    "data": json.dumps(event.to_dict()),
                }
        except Exception as e:
            yield {
                "data": json.dumps({"type": "error", "message": str(e)}),
            }

    return EventSourceResponse(event_generator())
