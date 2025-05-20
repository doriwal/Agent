# MySQL Agent

This module provides a MySQL agent that combines both predefined tools and tools dynamically loaded from a YAML configuration file.

## Features

- Load MySQL tools from YAML configuration files
- Support for SQL statements with parameters
- Fallback to generic query execution
- Integration with the main application

## How It Works

1. The agent first tries to use predefined tools loaded from the YAML configuration file
2. If no predefined tool matches, it falls back to the generic `run_query` method
3. The agent also provides utility tools like `list_tables` and `describe_table`
