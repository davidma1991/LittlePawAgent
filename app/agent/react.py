import json
from typing import Any, AsyncIterator

from app.agent.base import (
    BaseAgent, StreamEvent, ThinkingEvent, ToolStartEvent,
    ToolResultEvent, TokenEvent, DoneEvent, ErrorEvent
)
from app.agent.prompts import REACT_SYSTEM_PROMPT


class ReActAgent(BaseAgent):
    """ReAct loop agent: Reason → Act → Observe → Repeat until done."""

    MAX_ITERATIONS = 10

    async def run(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> AsyncIterator[StreamEvent]:
        messages = [
            {"role": "system", "content": REACT_SYSTEM_PROMPT},
            *conversation_history,
            {"role": "user", "content": user_message},
        ]

        enabled_tools = self.tools.list_enabled()
        tools_schema = [t.to_openai_schema() for t in enabled_tools] if enabled_tools else None

        for iteration in range(self.MAX_ITERATIONS):
            try:
                # Get response from Ollama (non-streaming when tools available)
                if tools_schema:
                    response = await self.llm.chat(
                        model=self.model,
                        messages=messages,
                        tools=tools_schema,
                        stream=False,
                    )
                    tool_calls = self.llm.parse_tool_calls(response)
                else:
                    tool_calls = None
                    response = None

                if tool_calls:
                    # Emit thinking
                    yield ThinkingEvent(content=f"Using {len(tool_calls)} tool(s)...")

                    # Add assistant message with tool calls
                    messages.append(response["choices"][0]["message"])

                    # Execute each tool call
                    for tc in tool_calls:
                        call_id = tc["id"] or f"call_{iteration}"
                        tool_name = tc["name"]
                        tool_args = tc["arguments"]

                        yield ToolStartEvent(
                            call_id=call_id,
                            tool=tool_name,
                            input=tool_args,
                        )

                        result = await self.tools.execute(tool_name, tool_args, call_id)

                        yield ToolResultEvent(
                            call_id=call_id,
                            tool=tool_name,
                            output=result.output,
                            error=result.error,
                        )

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps(result.output) if result.output is not None else (result.error or ""),
                        })

                    # Continue the loop to get the next response
                    continue

                else:
                    # No tool calls → stream the final answer
                    async for token in self.llm.chat_stream(
                        model=self.model,
                        messages=messages,
                    ):
                        yield TokenEvent(content=token)

                    yield DoneEvent()
                    return

            except Exception as e:
                yield ErrorEvent(message=str(e))
                return

        # Max iterations reached
        yield ErrorEvent(message="Maximum iterations reached without completing the task.")
