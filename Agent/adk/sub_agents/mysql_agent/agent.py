import os
import pathlib
import yaml
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.mcp_tool import MCPToolset
from mcp import StdioServerParameters
from typing import Tuple, List, Any, Dict, Optional

import config

load_dotenv()


def log_before_tool_modifier(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    print(f"[Callback] Before tool call for tool '{tool.name}' in agent '{tool_context.agent_name}' input args: {args}")
    return None


async def get_mysql_agent_tools_async() -> Tuple[List[Any], Any]:
    """Start MCP server for MySQL agent tools."""
    print("🔧 Starting MySQL Agent MCP Tool...")

    # Get the absolute path to the mysql_agent_mcp file
    script_dir = pathlib.Path(__file__).parent.absolute()
    script_path = os.path.join(script_dir, "mysql_agent_mcp.py")

    server_params = StdioServerParameters(
        command="python3",
        args=[script_path]
    )

    tools, exit_stack = await MCPToolset.from_server(connection_params=server_params)
    print(f"✅ MCP tools fetched. Found {len(tools)} tools.")
    return tools, exit_stack


def get_available_toolsets() -> List[str]:
    """Get the names of available toolsets from the YAML configuration."""
    # Path to the YAML configuration file
    config_dir = pathlib.Path(__file__).parent.parent.parent
    config_file = os.path.join(config_dir, "dynamic_tools", "mysql_tools.yaml")

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Get toolset names
        toolsets = config.get('toolsets', {})
        return list(toolsets.keys())
    except Exception as e:
        print(f"Error loading toolsets: {e}")
        return []


async def get_mysql_agent_async() -> Tuple[Agent, Any]:
    """Create and return a MySQL agent with both predefined and dynamic tools."""
    print(f"--- Creating MySQL Agent ---")

    # Get available toolsets
    toolset_names = get_available_toolsets()
    toolsets_str = ', '.join(toolset_names) if toolset_names else "None"
    print(f"Available toolsets: {toolsets_str}")

    # Get all tools
    tools, exit_stack = await get_mysql_agent_tools_async()

    # Get tool names for the instruction
    tool_names = [tool.name for tool in tools]
    dynamic_tools = [name for name in tool_names if name not in ['run_query', 'get_hotel_address', 'list_tables', 'describe_table']]
    dynamic_tools_str = ', '.join(dynamic_tools) if dynamic_tools else "None"

    # Create the agent
    agent = Agent(
        model=LiteLlm(model=config.model),
        name="mysql_assistant",
        description="MySQL database assistant capable of querying and describing data using both predefined and dynamic tools.",
        instruction=f"""
        You are a MySQL database expert. You can help users interact with their MySQL database by:

        1. Using predefined dynamic tools loaded from configuration:
           {dynamic_tools_str}

        2. Using standard tools:
           - Running SQL queries with `run_query(query)`
           - Listing available tables with `list_tables()`
           - Describing table structure with `describe_table(table_name)`
           - Getting hotel address by ID with `get_hotel_address(hotel_id)`


        Always:
        - Try to use the most specific tool for the job first
        - Fall back to the generic `run_query` tool if no specific tool matches
        - Provide clear explanations of query results
        - Format complex results in a readable way
        - Explain any errors encountered
        - Suggest improvements to queries when appropriate
        - Use proper SQL syntax and best practices
        """,
        tools=tools,
        before_tool_callback=log_before_tool_modifier
    )

    return agent, exit_stack
