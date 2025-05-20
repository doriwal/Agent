
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import MCPToolset
from mcp import StdioServerParameters
import config

load_dotenv()

# Elasticsearch MCP Tool
async def get_elasticsearch_tool_async():
    """tool is elasticsearch mcp server.
       Args:
            None

       Returns:
              tools: list of tools
              exit_stack: exit stack for cleanup
       """
    print(f"--- Tool: Elasticsearch ---")

    server_params = StdioServerParameters(
        command= "docker",
        args=[
            "run",
            "--rm",
            "-i",
            "mcp-elasticsearch",
            "--es-url", os.getenv("ES_URL"),
            "--ignore-cert-errors"
        ]
    )

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=server_params
    )

    print("MCP Toolset created successfully.")
    return tools, exit_stack

async def get_elasticsearch_agent_async():
    tools, exit_stack = await get_elasticsearch_tool_async()
    print(f"Fetched {len(tools)} tools from elasticSearch MCP server.")

    elasticsearch_agent = Agent(
        model=LiteLlm(model=config.model),
        name='elasticSearch_assistant',
        description=config.elasticsearch_agent_description,
        instruction=config.elasticsearch_agent_instruction,
        tools=tools,
        output_key="logs",
    )

    return elasticsearch_agent, exit_stack
