from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator


class StreamEvent(ABC):
    """Base event type for SSE streaming."""

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class ThinkingEvent(StreamEvent):
    content: str
    type: str = "thinking"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "content": self.content}


@dataclass
class PlanStep:
    id: str
    description: str
    status: str = "pending"  # pending | running | done | error


@dataclass
class PlanEvent(StreamEvent):
    steps: list[PlanStep]
    type: str = "plan"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "steps": [{"id": s.id, "description": s.description, "status": s.status} for s in self.steps],
        }


@dataclass
class PlanStepStartEvent(StreamEvent):
    step_id: str
    type: str = "plan_step_start"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "step_id": self.step_id}


@dataclass
class PlanStepDoneEvent(StreamEvent):
    step_id: str
    summary: str = ""
    type: str = "plan_step_done"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "step_id": self.step_id, "summary": self.summary}


@dataclass
class ToolStartEvent(StreamEvent):
    call_id: str
    tool: str
    input: dict[str, Any]
    type: str = "tool_start"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "call_id": self.call_id, "tool": self.tool, "input": self.input}


@dataclass
class ToolResultEvent(StreamEvent):
    call_id: str
    tool: str
    output: Any
    error: str | None = None
    type: str = "tool_result"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "call_id": self.call_id,
            "tool": self.tool,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class TokenEvent(StreamEvent):
    content: str
    type: str = "token"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "content": self.content}


@dataclass
class DoneEvent(StreamEvent):
    type: str = "done"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type}


@dataclass
class ErrorEvent(StreamEvent):
    message: str
    type: str = "error"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "message": self.message}


class BaseAgent(ABC):
    def __init__(self, ollama_client, tool_registry, model: str, config: dict[str, Any]):
        self.llm = ollama_client
        self.tools = tool_registry
        self.model = model
        self.config = config

    @abstractmethod
    async def run(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> AsyncIterator[StreamEvent]:
        """Run the agent and yield stream events."""
        ...
