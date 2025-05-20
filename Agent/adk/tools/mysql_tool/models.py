"""
Data models for dynamic tool loading.

This module provides data models for representing tool configurations.
"""

from typing import Dict, List, Any


class ToolConfig:
    """Configuration for a tool loaded from YAML."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a tool configuration.
        
        Args:
            name: The name of the tool
            config: The configuration dictionary for the tool
        """
        self.name = name
        self.config = config
        self.kind = config.get('kind')
        self.source_name = config.get('source')
        self.description = config.get('description', '')
        self.parameters = config.get('parameters', [])
        self.statement = config.get('statement', '')
    
    def __repr__(self) -> str:
        return f"ToolConfig(name={self.name}, kind={self.kind})"


class SourceConfig:
    """Configuration for a data source loaded from YAML."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a source configuration.
        
        Args:
            name: The name of the source
            config: The configuration dictionary for the source
        """
        self.name = name
        self.config = config
        self.kind = config.get('kind')
    
    def __repr__(self) -> str:
        return f"SourceConfig(name={self.name}, kind={self.kind})"


class ToolsetConfig:
    """Configuration for a toolset loaded from YAML."""
    
    def __init__(self, name: str, tool_names: List[str]):
        """
        Initialize a toolset configuration.
        
        Args:
            name: The name of the toolset
            tool_names: List of tool names in this toolset
        """
        self.name = name
        self.tool_names = tool_names
    
    def __repr__(self) -> str:
        return f"ToolsetConfig(name={self.name}, tools={self.tool_names})"
