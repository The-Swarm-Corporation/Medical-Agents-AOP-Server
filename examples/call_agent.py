import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


AOP_URL = os.environ.get("AOP_URL", "http://localhost:8000/mcp")


async def main() -> None:
    # Configure via environment variables (no CLI)
    # Required
    agent_name = os.environ.get("AGENT_NAME", "Blood-Data-Analysis-Agent")
    task = os.environ.get("AGENT_TASK", "Interpret this CBC: WBC 15.2, HGB 10.1, PLT 420")
    # Optional
    img = os.environ.get("AGENT_IMG")
    imgs_env = os.environ.get("AGENT_IMGS")  # comma-separated paths/URIs
    correct_answer = os.environ.get("AGENT_CORRECT_ANSWER")

    payload = {"task": task}
    if img:
        payload["img"] = img
    if imgs_env:
        imgs = [p.strip() for p in imgs_env.split(",") if p.strip()]
        if imgs:
            payload["imgs"] = imgs
    if correct_answer:
        payload["correct_answer"] = correct_answer

    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(agent_name, arguments=payload)
            print("Agent result:")
            print(result)  # CallToolResult


if __name__ == "__main__":
    asyncio.run(main())


