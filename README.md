# Medical Agents AOP Server

A production‑ready template for deploying multiple specialized medical agents as MCP tools using the AOP (Agent Orchestration Protocol) from the `swarms` library. This server exposes agents as callable tools that any MCP‑compatible client can discover and execute.

## What You Get

- Multiple domain‑focused medical agents (labs, ICD‑10 mapping, treatment options, drug interactions, imaging triage, clinical note summarization)
- A single AOP server that registers each agent as an MCP tool
- Sensible defaults, safety language, and structured outputs
- Clear examples for customization and MCP client usage

## Prerequisites

- Python 3.9+ recommended
- `pip` available in your environment
- Access to model providers required by the chosen `model_name` values (e.g., Anthropic for `claude-haiku-4-5`); configure credentials per provider documentation

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
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

### Discovering and Selecting Tools (Client‑Side)

If you’re building a Python client, you can use `AOPCluster` to discover tools across one or more servers:

```python
from swarms.structs.aop import AOPCluster

cluster = AOPCluster(
    urls=["http://localhost:8000/mcp"],
    transport="streamable-http",
)

all_tools = cluster.get_tools(output_type="dict")
research_tool_info = cluster.find_tool_by_server_name("Blood-Data-Analysis-Agent")
```

You can then call the corresponding MCP tool by name in your MCP‑compatible client with the appropriate arguments. For example, conceptually:

```python
# Pseudocode – your MCP client will provide the concrete API
call_tool(
  name="Blood-Data-Analysis-Agent",
  arguments={"task": "Interpret this CBC: ..."}
)
```

### Example Calls (Conceptual)

```python
# Lab analysis
call_tool(
  name="Blood-Data-Analysis-Agent",
  arguments={"task": "Interpret this CBC with elevated WBC and low HGB..."}
)

# ICD-10 mapping
call_tool(
  name="ICD10-Symptom-Mapper-Agent",
  arguments={"task": "Adult with acute left lower quadrant abdominal pain 24h..."}
)

# Treatment options
call_tool(
  name="Treatment-Solutions-Agent",
  arguments={"task": "Non-directive overview of options for mild persistent asthma"}
)

# Drug interactions
call_tool(
  name="Drug-Interaction-Agent",
  arguments={"task": "Check interactions between sertraline, tramadol, and supplements"}
)

# Imaging triage
call_tool(
  name="Imaging-Triage-Agent",
  arguments={"task": "CXR: 'Right lower lobe opacity' – plain-language context"}
)

# Clinical note summarization
call_tool(
  name="Clinical-Note-Summarizer-Agent",
  arguments={"task": "Summarize SOAP note; list meds, problems, gaps"}
)
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
