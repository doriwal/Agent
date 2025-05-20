"""
Dynamic Tool Loader for ADK.

This module provides functionality to dynamically load tools from a YAML configuration file.
It supports MySQL database tools with configurable SQL statements.
"""

import os
import yaml
import logging
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union
from contextlib import AsyncExitStack

from google.adk.tools import BaseTool
from google.adk.tools.mcp_tool import MCPToolset
from mcp import StdioServerParameters

from adk.tools.mysql_tool.models import ToolConfig, SourceConfig, ToolsetConfig

# Import after models to avoid circular imports
from adk.tools.mysql_tool.mysql_tool_generator import DynamicMySQLMCPGenerator

logger = logging.getLogger(__name__)


class ToolFactory:
    """Factory for creating tools from configurations."""

    @staticmethod
    async def create_mysql_tool(tool_config: ToolConfig, source_config: SourceConfig) -> Tuple[List[BaseTool], AsyncExitStack]:
        """
        Create a MySQL tool using MCP.

        Args:
            tool_config: The tool configuration
            source_config: The source configuration

        Returns:
            A tuple of (tools, exit_stack)
        """
        # Extract source configuration
        host = source_config.config.get('host', 'localhost')
        port = source_config.config.get('port', 3306)
        database = source_config.config.get('database', '')
        user = source_config.config.get('user', '')
        password = source_config.config.get('password', '')

        # Create environment variables for the MCP server
        env = {
            "MYSQL_HOST": host,
            "MYSQL_PORT": str(port),
            "MYSQL_DATABASE": database,
            "MYSQL_USER": user,
            "MYSQL_PASSWORD": password,
        }

        # Set up MCP server parameters
        server_params = StdioServerParameters(
            command="python",
            args=["sub_agents/mysql_mcp/mysql_mcp.py"],
            env=env
        )

        # Create MCP toolset
        tools, exit_stack = await MCPToolset.from_server(connection_params=server_params)
        logger.info(f"Created MySQL MCP tool: {tool_config.name}")
        return tools, exit_stack


class ToolLoader:
    """Loads tools from a YAML configuration file."""

    def __init__(self, config_file: str):
        """
        Initialize the tool loader.

        Args:
            config_file: Path to the YAML configuration file
        """
        self.config_file = config_file
        self.sources: Dict[str, SourceConfig] = {}
        self.tools: Dict[str, ToolConfig] = {}
        self.toolsets: Dict[str, ToolsetConfig] = {}
        self._load_config()

    def _load_config(self):
        """Load the configuration from the YAML file."""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)

            # Load sources
            sources_config = config.get('sources', {})
            for name, source_config in sources_config.items():
                self.sources[name] = SourceConfig(name, source_config)

            # Load tools
            tools_config = config.get('tools', {})
            for name, tool_config in tools_config.items():
                self.tools[name] = ToolConfig(name, tool_config)

            # Load toolsets
            toolsets_config = config.get('toolsets', {})
            for name, tool_names in toolsets_config.items():
                self.toolsets[name] = ToolsetConfig(name, tool_names)

            logger.info(f"Loaded configuration from {self.config_file}")
            logger.info(f"Found {len(self.sources)} sources, {len(self.tools)} tools, and {len(self.toolsets)} toolsets")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    async def load_tool(self, tool_name: str) -> Tuple[List[BaseTool], AsyncExitStack]:
        """
        Load a specific tool by name.

        Args:
            tool_name: The name of the tool to load

        Returns:
            A tuple of (tools, exit_stack)
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found in configuration")

        tool_config = self.tools[tool_name]
        source_name = tool_config.source_name

        if source_name not in self.sources:
            raise ValueError(f"Source {source_name} not found for tool {tool_name}")

        source_config = self.sources[source_name]

        # Create the tool based on its kind
        if tool_config.kind == 'mysql-sql':
            return await ToolFactory.create_mysql_tool(tool_config, source_config)
        else:
            raise ValueError(f"Unsupported tool kind: {tool_config.kind}")

    async def load_toolset(self, toolset_names: Union[str, List[str]]) -> Tuple[List[BaseTool], List[AsyncExitStack]]:
        """
        Load one or more toolsets by name.

        Args:
            toolset_names: A toolset name or list of toolset names to load

        Returns:
            A tuple of (tools, exit_stacks)
        """
        # Convert single toolset name to list for consistent processing
        if isinstance(toolset_names, str):
            toolset_names = [toolset_names]

        # Validate all toolset names before processing
        for toolset_name in toolset_names:
            if toolset_name not in self.toolsets:
                raise ValueError(f"Toolset {toolset_name} not found in configuration")

        all_tools = []
        all_exit_stacks = []
        script_paths = []

        # Process each toolset
        for toolset_name in toolset_names:
            toolset_config = self.toolsets[toolset_name]

            # Generate a dynamic MCP server for all tools in the toolset
            tool_configs = []
            source_configs = set()

            # Collect all tool configurations and their sources for this toolset
            for tool_name in toolset_config.tool_names:
                if tool_name not in self.tools:
                    raise ValueError(f"Tool {tool_name} not found in configuration")

                tool_config = self.tools[tool_name]
                source_name = tool_config.source_name

                if source_name not in self.sources:
                    raise ValueError(f"Source {source_name} not found for tool {tool_name}")

                source_config = self.sources[source_name]
                source_configs.add(source_config.kind)

                tool_configs.append(tool_config)

            # Skip empty toolsets
            if not tool_configs:
                logger.warning(f"Toolset {toolset_name} has no tools, skipping")
                continue

            # Check if all tools use the same type of source
            if len(source_configs) != 1:
                raise ValueError(f"All tools in toolset {toolset_name} must use the same type of source. Found: {source_configs}")

            source_type = next(iter(source_configs))

            # Generate and run the appropriate MCP server based on source type
            if source_type == 'mysql':
                # Get the first tool's source config (they all use the same source type)
                source_name = tool_configs[0].source_name
                source_config = self.sources[source_name]

                # Generate a dynamic MCP script
                script_path = DynamicMySQLMCPGenerator.create_temp_script_file(tool_configs)
                script_paths.append(script_path)

                try:
                    # Extract source configuration
                    host = source_config.config.get('host', 'localhost')
                    port = source_config.config.get('port', 3306)
                    database = source_config.config.get('database', '')
                    user = source_config.config.get('user', '')
                    password = source_config.config.get('password', '')

                    # Create environment variables for the MCP server
                    env = {
                        "MYSQL_HOST": host,
                        "MYSQL_PORT": str(port),
                        "MYSQL_DATABASE": database,
                        "MYSQL_USER": user,
                        "MYSQL_PASSWORD": password,
                    }

                    # Set up MCP server parameters
                    server_params = StdioServerParameters(
                        command="python",
                        args=[script_path],
                        env=env
                    )

                    # Create MCP toolset
                    tools, exit_stack = await MCPToolset.from_server(connection_params=server_params)
                    logger.info(f"Created dynamic MySQL MCP toolset: {toolset_name} with {len(tools)} tools")

                    # Register cleanup for the script file when the exit stack is closed
                    exit_stack.callback(lambda p=script_path: os.unlink(p))

                    all_tools.extend(tools)
                    all_exit_stacks.append(exit_stack)
                except Exception as e:
                    logger.error(f"Error creating dynamic MySQL MCP toolset for {toolset_name}: {e}")
                    # Clean up the temporary file
                    try:
                        os.unlink(script_path)
                    except Exception:
                        pass
                    raise
            else:
                raise ValueError(f"Unsupported source type: {source_type} for toolset {toolset_name}")

        return all_tools, all_exit_stacks
