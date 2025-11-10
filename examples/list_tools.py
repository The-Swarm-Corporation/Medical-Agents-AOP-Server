import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


AOP_URL = os.environ.get("AOP_URL", "http://localhost:8000/mcp")


async def main() -> None:
    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools:")
            for t in tools.tools:
                print(f"- {t.name}: {t.description or ''}")


if __name__ == "__main__":
    asyncio.run(main())


