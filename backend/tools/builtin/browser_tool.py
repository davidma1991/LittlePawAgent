from backend.tools.base import ToolDef


def make_browser_tool(
    headless: bool = True,
    ollama_base_url: str = "http://localhost:11434",
    ollama_model: str = "llama3.2",
) -> ToolDef:
    async def handler(task: str) -> str:
        try:
            from browser_use import Agent as BrowserAgent
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=ollama_model,
                base_url=f"{ollama_base_url}/v1",
                api_key="ollama",
            )
            agent = BrowserAgent(task=task, llm=llm)
            result = await agent.run()
            return result.final_result() or "Browser task completed but no result returned."
        except ImportError:
            return "browser-use is not installed. Install it with: pip install browser-use"
        except Exception as e:
            return f"Browser error: {str(e)}"

    return ToolDef(
        name="browser_use",
        description="Use a web browser to navigate websites, extract information, fill forms, and interact with web applications.",
        parameters={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Natural language description of what to do in the browser",
                },
            },
            "required": ["task"],
        },
        handler=handler,
        source="builtin",
    )
