import json
from typing import Any, AsyncIterator

from backend.agent.base import (
    BaseAgent, StreamEvent, ThinkingEvent, PlanEvent, PlanStep,
    PlanStepStartEvent, PlanStepDoneEvent, ToolStartEvent,
    ToolResultEvent, TokenEvent, DoneEvent, ErrorEvent
)
from backend.agent.prompts import (
    PLAN_EXECUTE_SYSTEM_PROMPT, PLANNER_PROMPT, SYNTHESIZER_PROMPT, STEP_PROMPT
)


class PlanExecuteAgent(BaseAgent):
    """Plan-then-Execute agent: Creates a plan, executes each step with mini-ReAct, synthesizes."""

    MAX_STEP_ITERATIONS = 5

    async def run(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> AsyncIterator[StreamEvent]:
        # Step 1: Generate the plan
        yield ThinkingEvent(content="Creating a plan...")

        try:
            plan = await self._generate_plan(user_message)
        except Exception as e:
            yield ErrorEvent(message=f"Failed to create plan: {e}")
            return

        if not plan:
            # Fallback to simple response
            async for token in self.llm.chat_stream(
                model=self.model,
                messages=[
                    {"role": "system", "content": PLAN_EXECUTE_SYSTEM_PROMPT},
                    *conversation_history,
                    {"role": "user", "content": user_message},
                ],
            ):
                yield TokenEvent(content=token)
            yield DoneEvent()
            return

        yield PlanEvent(steps=plan)

        # Step 2: Execute each step
        step_results = []
        enabled_tools = self.tools.list_enabled()
        tools_schema = [t.to_openai_schema() for t in enabled_tools] if enabled_tools else None

        for step in plan:
            yield PlanStepStartEvent(step_id=step.id)

            step_summary = ""
            try:
                async for event in self._execute_step(
                    step=step,
                    goal=user_message,
                    previous_results=step_results,
                    tools_schema=tools_schema,
                ):
                    if isinstance(event, TokenEvent):
                        step_summary += event.content
                    yield event
            except Exception as e:
                step_summary = f"Error: {e}"
                yield ErrorEvent(message=f"Step {step.id} failed: {e}")

            step_results.append({"step": step.description, "result": step_summary})
            yield PlanStepDoneEvent(step_id=step.id, summary=step_summary[:200])

        # Step 3: Synthesize final answer
        yield ThinkingEvent(content="Synthesizing results...")

        results_text = "\n".join(
            f"Step {i+1} ({r['step']}): {r['result']}" for i, r in enumerate(step_results)
        )

        synth_messages = [
            {"role": "system", "content": PLAN_EXECUTE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": SYNTHESIZER_PROMPT.format(
                    question=user_message,
                    step_results=results_text,
                ),
            },
        ]

        async for token in self.llm.chat_stream(model=self.model, messages=synth_messages):
            yield TokenEvent(content=token)

        yield DoneEvent()

    async def _generate_plan(self, task: str) -> list[PlanStep] | None:
        """Ask Ollama to generate a structured plan."""
        messages = [
            {"role": "system", "content": PLAN_EXECUTE_SYSTEM_PROMPT},
            {"role": "user", "content": PLANNER_PROMPT.format(task=task)},
        ]

        response = await self.llm.chat(model=self.model, messages=messages)
        content = self.llm.get_content(response)

        # Try to parse JSON from the response
        try:
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)
            steps = data.get("steps", [])
            return [
                PlanStep(id=str(s.get("id", i+1)), description=s.get("description", ""))
                for i, s in enumerate(steps)
            ]
        except (json.JSONDecodeError, KeyError):
            return None

    async def _execute_step(
        self,
        step: PlanStep,
        goal: str,
        previous_results: list[dict],
        tools_schema: list[dict] | None,
    ) -> AsyncIterator[StreamEvent]:
        """Mini ReAct loop for a single step."""
        prev_results_text = "\n".join(
            f"- {r['step']}: {r['result'][:300]}" for r in previous_results
        ) or "None"

        messages = [
            {"role": "system", "content": PLAN_EXECUTE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": STEP_PROMPT.format(
                    goal=goal,
                    step_description=step.description,
                    previous_results=prev_results_text,
                ),
            },
        ]

        for iteration in range(self.MAX_STEP_ITERATIONS):
            if tools_schema:
                response = await self.llm.chat(
                    model=self.model,
                    messages=messages,
                    tools=tools_schema,
                )
                tool_calls = self.llm.parse_tool_calls(response)
            else:
                tool_calls = None
                response = None

            if tool_calls:
                messages.append(response["choices"][0]["message"])

                for tc in tool_calls:
                    call_id = tc["id"] or f"step_{step.id}_{iteration}"
                    yield ToolStartEvent(call_id=call_id, tool=tc["name"], input=tc["arguments"])
                    result = await self.tools.execute(tc["name"], tc["arguments"], call_id)
                    yield ToolResultEvent(
                        call_id=call_id,
                        tool=tc["name"],
                        output=result.output,
                        error=result.error,
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": json.dumps(result.output) if result.output is not None else (result.error or ""),
                    })
                continue
            else:
                async for token in self.llm.chat_stream(model=self.model, messages=messages):
                    yield TokenEvent(content=token)
                return
