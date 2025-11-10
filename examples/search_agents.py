import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


AOP_URL = os.environ.get("AOP_URL", "http://localhost:8000/mcp")


async def main() -> None:
    query = os.environ.get("SEARCH_QUERY", "research")
    fields_env = os.environ.get("SEARCH_FIELDS")  # comma-separated fields
    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            if "search_agents" not in names:
                print("search_agents tool not available on server.")
                return

            payload = {"query": query}
            if fields_env:
                fields = [f.strip() for f in fields_env.split(",") if f.strip()]
                if fields:
                    payload["search_fields"] = fields

            resp = await session.call_tool("search_agents", payload)
            print(resp)


if __name__ == "__main__":
    asyncio.run(main())


