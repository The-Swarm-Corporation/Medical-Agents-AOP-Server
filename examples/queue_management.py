import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


AOP_URL = os.environ.get("AOP_URL", "http://localhost:8000/mcp")


async def main() -> None:
    agent_name = os.environ.get("AGENT_NAME", "Blood-Data-Analysis-Agent")
    action = os.environ.get("QUEUE_ACTION", "stats").lower()  # stats|pause|resume|clear
    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # We detect presence of management tools and call them
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}

            if action == "stats":
                if "get_queue_stats" in names:
                    resp = await session.call_tool("get_queue_stats", {"agent_name": agent_name})
                    print(resp)
                else:
                    print("get_queue_stats tool not available on server.")
            elif action == "pause":
                if "pause_agent_queue" in names:
                    resp = await session.call_tool("pause_agent_queue", {"agent_name": agent_name})
                    print(resp)
                else:
                    print("pause_agent_queue tool not available on server.")
            elif action == "resume":
                if "resume_agent_queue" in names:
                    resp = await session.call_tool("resume_agent_queue", {"agent_name": agent_name})
                    print(resp)
                else:
                    print("resume_agent_queue tool not available on server.")
            elif action == "clear":
                if "clear_agent_queue" in names:
                    resp = await session.call_tool("clear_agent_queue", {"agent_name": agent_name})
                    print(resp)
                else:
                    print("clear_agent_queue tool not available on server.")


if __name__ == "__main__":
    asyncio.run(main())


