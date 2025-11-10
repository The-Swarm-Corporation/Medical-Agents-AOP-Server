import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


AOP_URL = "https://medical-agents-aop-server-production.up.railway.app/mcp"
# AOP_URL = "http://localhost:8000/mcp"


async def main() -> None:
    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Basic "server info": list available tools
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("Available tools:", names)

            # If AOP discovery tools are exposed, show agent list as "server info"
            if "list_agents" in {t.name for t in tools.tools}:
                result = await session.call_tool("list_agents", {})
                # Prefer structured content when available
                if getattr(result, "structuredContent", None):
                    print("AOP agent names:", result.structuredContent)
                else:
                    print("AOP list_agents result:", result)


if __name__ == "__main__":
    asyncio.run(main())


