# MCP Client Examples

These examples show how to use the official `mcp` Python client to interact with the AOP server in this repo.

## Setup

```bash
pip install mcp
```

By default, examples connect to `http://localhost:8000/mcp`. Override with:

```bash
export AOP_URL="http://localhost:8010/mcp"
```

## Scripts

- `get_server_info.py`: Print server info (name, description, etc.)
- `list_tools.py`: List all registered tools (agents)
- `call_agent.py`: Call a specific agent by name with a `task`
- `discover_and_call.py`: Discover agents, inspect details, and call one
- `queue_management.py`: Show queue stats, pause/resume a specific agent queue
- `search_agents.py`: Search agents by keywords

## Usage

```bash
# Get server info
python examples/get_server_info.py

# List tools
python examples/list_tools.py

# Call an agent (configure via env, no CLI)
export AGENT_NAME="Blood-Data-Analysis-Agent"
export AGENT_TASK="Interpret this CBC..."
# optional:
# export AGENT_IMG="/path/to/image.png"
# export AGENT_IMGS="/path/a.png,/path/b.png"
# export AGENT_CORRECT_ANSWER="..."
python examples/call_agent.py

# Discover agents and call one (configure via env, no CLI)
export PREFER_TAG="research"
export FALLBACK_NAME="Blood-Data-Analysis-Agent"
export TASK="Provide a brief summary of CBC interpretation basics."
python examples/discover_and_call.py

# Queue management for a specific agent (configure via env, no CLI)
export AGENT_NAME="Blood-Data-Analysis-Agent"
export QUEUE_ACTION="stats"   # stats|pause|resume|clear
python examples/queue_management.py

# Search agents by keyword across name/description/tags/capabilities (configure via env)
export SEARCH_QUERY="research"
# optional: export SEARCH_FIELDS="name,description,tags,capabilities"
python examples/search_agents.py
```


