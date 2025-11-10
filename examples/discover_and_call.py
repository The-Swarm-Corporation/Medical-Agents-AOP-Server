import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


AOP_URL = os.environ.get("AOP_URL", "http://localhost:8000/mcp")


async def main() -> None:
    prefer_tag = os.environ.get("PREFER_TAG")  # e.g., "research"
    fallback_name = os.environ.get("FALLBACK_NAME")  # tool name
    task = os.environ.get("TASK", "Provide a brief summary of CBC interpretation basics.")
    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
        # Find discovery helpers if present
        tool_names = {t.name for t in tools.tools}

            chosen = None

        # Try to use discover_agents (if provided by the server)
            if "discover_agents" in tool_names:
                resp = await session.call_tool("discover_agents", arguments={})
                agents = getattr(resp, "structuredContent", None)
                if agents and prefer_tag:
                    for a in agents:
                        tags = a.get("tags", [])
                        if prefer_tag in tags:
                            chosen = a.get("tool_name") or a.get("agent_name")
                            break
                if not chosen and agents:
                    chosen = (agents[0].get("tool_name") or agents[0].get("agent_name"))

        # Fallback: choose first non-management tool if discovery not available
        if not chosen:
            # Filter out known management tool names heuristically
            mgmt = {
                "discover_agents", "get_agent_details", "get_agents_info", "list_agents",
                "search_agents", "get_queue_stats", "pause_agent_queue",
                "resume_agent_queue", "clear_agent_queue", "get_task_status",
            }
            ordered = [t.name for t in tools.tools]
            ordered = [n for n in ordered if n and n not in mgmt]
            if ordered:
                chosen = ordered[0]

        if not chosen and fallback_name:
            chosen = fallback_name

        if not chosen:
            print("No suitable agent found to call.")
            return

        print(f"Calling agent: {chosen}")
        result = await session.call_tool(chosen, arguments={"task": task})
        print("Result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())


