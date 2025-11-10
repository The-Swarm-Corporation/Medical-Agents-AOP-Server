# Medical Agents AOP Server

A production‑ready template for deploying multiple specialized medical agents as MCP tools using the AOP (Agent Orchestration Protocol) from the `swarms` library. This server exposes agents as callable tools that any MCP‑compatible client can discover and execute.

## What You Get

- Multiple domain‑focused medical agents (labs, ICD‑10 mapping, treatment options, drug interactions, imaging triage, clinical note summarization)
- A single AOP server that registers each agent as an MCP tool
- Sensible defaults, safety language, and structured outputs
- Clear examples for customization and MCP client usage

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start: Run the Server

This repository ships with a ready‑to‑run server in `app.py` that registers six medical agents.

```bash
python app.py
```

By default, the server starts on port `8000` and registers each agent as an MCP tool using the agent’s `agent_name`. You should see logs indicating the server name (`MedicalAgentServer`) and registered tools.

## Customizing AOP Settings (Port, Host, Logging, Queue)

In `app.py`, the AOP instance is created like this:

```python
deployer = AOP(
    server_name="MedicalAgentServer",
    description="...",
    port=8000,
    verbose=True,
    log_level="INFO",
)
```

You can adjust:
- `port`: Change the listening port (e.g., `port=8010`)
- `host`: Bind externally (e.g., `host="0.0.0.0"`)
- `verbose` and `log_level`: Increase/decrease logging (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`)
- Queue options for higher throughput:
  - `queue_enabled=True`
  - `max_workers_per_agent=2`
  - `max_queue_size_per_agent=500`
  - `processing_timeout=60`
  - `retry_delay=2.0`

Example:

```python
deployer = AOP(
    server_name="MedicalAgentServer",
    port=8010,
    host="0.0.0.0",
    verbose=True,
    log_level="DEBUG",
    queue_enabled=True,
    max_workers_per_agent=2,
    max_queue_size_per_agent=500,
    processing_timeout=60,
    retry_delay=2.0,
)
```

## Add or Modify Agents

Agents are defined with clear system prompts and metadata, then added to the server. You can add one agent or many at once.

Minimal example (single agent):

```python
from swarms import Agent

my_agent = Agent(
  agent_name="My-Custom-Agent",
  agent_description="Explains X and summarizes Y for educational purposes",
  model_name="claude-haiku-4-5",
  max_loops=1,
  dynamic_temperature_enabled=True,
  system_prompt="""You are a helpful specialist...""",
  tags=["custom"],
  capabilities=["explanation"],
  role="worker",
)

deployer.add_agent(my_agent)
```

Batch registration (as used in this repo):

```python
agents = [agent_a, agent_b, agent_c]
deployer.add_agents_batch(agents)
```

Tool naming:
- By default, the tool name equals `agent.agent_name`. Choose descriptive, stable names (e.g., `"Blood-Data-Analysis-Agent"`).
- You can override the tool name and description with `add_agent(agent, tool_name="...", tool_description="...")`.

## How to Use the Agents Through MCP

Once running, each agent is exposed as an MCP tool. All tools accept a common parameter set:

- `task` (required): The main instruction or prompt
- `img` (optional): Single image path/URI
- `imgs` (optional): List of image paths/URIs
- `correct_answer` (optional): For validation or comparison

All tools return:

```json
{
  "result": "string",
  "success": true,
  "error": null
}
```

## Using the MCP Python Client (Official)

You can connect to this AOP server with the official `mcp` Python client (streamable HTTP transport) to discover tools and call agents.

Install:

```bash
pip install mcp
```

List tools and call an agent:

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

AOP_URL = "http://localhost:8000/mcp"  # adjust if you changed host/port

async def main():
    async with streamablehttp_client(AOP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1) List available tools (registered agents)
            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            # 2) Call a specific agent by tool name
            tool_name = "Blood-Data-Analysis-Agent"  # replace with any agent name you registered
            result = await session.call_tool(
                tool_name,
                arguments={
                    "task": "Interpret this CBC: WBC 15.2, HGB 10.1, PLT 420",
                    # Optional extras per this server's schema:
                    # "img": "/path/to/image.png",
                    # "imgs": ["/path/a.png", "/path/b.png"],
                    # "correct_answer": "..."
                },
            )
            print("Agent result:", result)  # CallToolResult

asyncio.run(main())
```

Notes:
- `AOP_URL` defaults to `http://localhost:8000/mcp` based on this repo’s server config.
- All agents share the same input parameters: `task` (required), plus optional `img`, `imgs`, `correct_answer`.

## Examples (MCP client)

This repo includes runnable examples using the official MCP streamable HTTP client in `examples/`.

- `examples/get_server_info.py`: Print available tools and, if exposed, AOP agent names
- `examples/list_tools.py`: List all registered tools (agents)
- `examples/call_agent.py`: Call a specific agent by name with a `task`
- `examples/discover_and_call.py`: Discover agents and call one (prefers a tag if provided)
- `examples/queue_management.py`: Show/pause/resume/clear queue for a specific agent
- `examples/search_agents.py`: Search agents by keywords/fields

Setup:

```bash
pip install -r requirements.txt
# optional: point to a different server
export AOP_URL="http://localhost:8000/mcp"
```

Run:

```bash
# List tools
python examples/list_tools.py

# Call an agent (configure via env, no CLI flags)
export AGENT_NAME="Blood-Data-Analysis-Agent"
export AGENT_TASK="Interpret this CBC..."
# optional:
# export AGENT_IMG="/path/to/image.png"
# export AGENT_IMGS="/path/a.png,/path/b.png"
# export AGENT_CORRECT_ANSWER="..."
python examples/call_agent.py

# Discover agents and call one (configure via env)
export PREFER_TAG="research"
export FALLBACK_NAME="Blood-Data-Analysis-Agent"
export TASK="Provide a brief summary of CBC interpretation basics."
python examples/discover_and_call.py

# Queue management (stats|pause|resume|clear)
export AGENT_NAME="Blood-Data-Analysis-Agent"
export QUEUE_ACTION="stats"
python examples/queue_management.py

# Search agents (configure via env)
export SEARCH_QUERY="research"
# optional: export SEARCH_FIELDS="name,description,tags,capabilities"
python examples/search_agents.py
```

## Discovery and Queue Management Tools

When queue‑based execution is enabled, the server also exposes management and discovery tools that MCP clients can call:

- `discover_agents(agent_name: Optional[str])`: Get information about agents (name, description, tags, capabilities)
- `get_agent_details(agent_name: str)`: Detailed agent configuration and discovery info
- `get_agents_info(agent_names: List[str])`: Bulk details for multiple agents
- `list_agents()`: List of available agent names
- `search_agents(query: str, search_fields: Optional[List[str]])`: Keyword search
- `get_queue_stats(agent_name: Optional[str])`: Queue statistics
- `pause_agent_queue(agent_name: str)`, `resume_agent_queue(agent_name: str)`, `clear_agent_queue(agent_name: str)`
- `get_task_status(agent_name: str, task_id: str)`

These are useful for dynamic agent discovery, monitoring, and operational control in multi‑agent workflows.

## Safety and Scope

- All agents are designed for educational, non‑diagnostic output
- Responses avoid directives and emphasize uncertainty when appropriate
- Always validate outputs with licensed clinicians and authoritative sources

## Troubleshooting

- Port already in use: Change `port` in the AOP constructor or free the port
- Authentication/Models: Ensure your environment is configured for the specified `model_name` (API keys, endpoints)
- Tool not visible in client: Confirm the server is reachable from the client and that the agent was registered (logs, `list_agents`)
- High throughput: Enable queue settings and increase `max_workers_per_agent`

## License

This project is licensed under the terms specified in `LICENSE`.

## References

- AOP classes and methods in `swarms.structs.aop` (this repository mirrors capabilities in `docs.txt`)
- See `app.py` for concrete agent definitions and server setup
