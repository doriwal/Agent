"""
Dynamic Tools package for ADK.

This package provides functionality to dynamically load tools from YAML configuration files.
"""

# Define __all__ to control what's imported with 'from package import *'
__all__ = [
    'ToolLoader',
    'ToolConfig',
    'SourceConfig',
    'ToolsetConfig',
    'DynamicMySQLMCPGenerator',
]

# Import the models first to avoid circular imports
try:
    from adk.tools.mysql_tool.models import ToolConfig, SourceConfig, ToolsetConfig
    from adk.tools.mysql_tool.tool_loader import ToolLoader
    from adk.tools.mysql_tool.mysql_tool_generator import DynamicMySQLMCPGenerator
except ImportError as e:
    # Log the import error but don't crash the module
    import logging
    logging.getLogger(__name__).warning(f"Error importing dynamic tools: {e}")
