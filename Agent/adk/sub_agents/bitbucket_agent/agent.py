import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import MCPToolset
from mcp import StdioServerParameters
import config

load_dotenv()

async def get_bitbucket_tool_async():
    """tool is bitbucket mcp server.
       Args:
           None

       Returns:
              tools: list of tools
              exit_stack: exit stack for cleanup
       """
    print(f"--- Tool: Bitbucket ---")

    # MCP server run as a docker container
    server_params = StdioServerParameters(
        command= "docker",
        args= [
            "run",
            "--rm",
            "-i",
            "mcp-bitbucket",
            "--username",os.getenv("BITBUCKET_USERNAME"),
            "--app-password", os.getenv("BITBUCKET_PASSWORD")
        ]
    )

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=server_params
    )

    print("MCP Toolset created successfully.")
    return tools, exit_stack


async def get_bitbucket_agent_async():
    tools, exit_stack = await get_bitbucket_tool_async()
    print(f"Fetched {len(tools)} tools from bitbucket MCP server.")

    bitbucket_agent = Agent(
        model=LiteLlm(model=config.model),
        name='bitbucket_assistant',
        description=config.bitbucket_agent_description,
        instruction=config.bitbucket_agent_instruction,
        tools=tools,
        output_key="code",
    )

    return bitbucket_agent, exit_stack
