#!/usr/bin/env python3
import os
import yaml
import pathlib
import mysql.connector
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import Dict, Any

load_dotenv()

mcp = FastMCP(name="MySQLAgentServer")

# MySQL connection function
def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT")),
    )

# Load dynamic tools from YAML configuration
def load_dynamic_tools_from_yaml():
    """Load dynamic tools from the YAML configuration file."""
    # Path to the YAML configuration file
    config_dir = pathlib.Path(__file__).parent.parent.parent
    config_file = os.path.join(config_dir, "dynamic_tools", "mysql_tools.yaml")
    print(f"Loading dynamic tools from: {config_file}")

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Load tools
        tools_config = config.get('tools', {})

        # Register each tool
        for tool_name, tool_config in tools_config.items():
            if tool_config.get('kind') == 'mysql-sql':
                register_dynamic_tool(tool_name, tool_config)

        print(f"Loaded {len(tools_config)} dynamic tools from YAML configuration")
    except Exception as e:
        print(f"Error loading dynamic tools: {e}")

def register_dynamic_tool(tool_name: str, tool_config: Dict[str, Any]):
    """Register a dynamic tool with the MCP server."""
    # Create function name from tool name
    func_name = tool_name.replace('-', '_')

    # Get tool description
    description = tool_config.get('description', f"Dynamic SQL tool: {tool_name}")

    # Get SQL statement
    sql_statement = tool_config.get('statement', '')
    if not sql_statement:
        print(f"Warning: No SQL statement defined for tool {tool_name}")
        return

    # Get parameters
    parameters = tool_config.get('parameters', [])
    param_names = [p.get('name') for p in parameters]

    # Create the dynamic function
    def dynamic_tool(*args, **kwargs):
        """Dynamically generated SQL tool."""
        conn = get_mysql_connection()
        cursor = conn.cursor()

        # Map positional args to named parameters
        param_values = args

        # Replace $1, $2, etc. with %s for MySQL
        query = sql_statement
        for i in range(len(param_names), 0, -1):
            query = query.replace(f"${i}", "%s")

        # Execute the query with parameters
        if param_values:
            if len(param_values) == 1:
                cursor.execute(query, (param_values[0],))
            else:
                cursor.execute(query, param_values)
        else:
            cursor.execute(query)

        try:
            result = cursor.fetchall()
            return str(result)
        except mysql.connector.InterfaceError:
            return "Query executed successfully."
        finally:
            cursor.close()
            conn.close()

    # Set the function name and docstring
    dynamic_tool.__name__ = func_name
    dynamic_tool.__doc__ = description

    # Register the function with the MCP server
    mcp.tool()(dynamic_tool)

    print(f"Registered dynamic tool: {tool_name}")

# Load dynamic tools before defining static tools
load_dynamic_tools_from_yaml()

# Define static tools
# These will be used as fallbacks if no dynamic tool matches

@mcp.tool()
def run_query(query: str) -> str:
    """Run a SQL query on the configured MySQL database."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    try:
        result = cursor.fetchall()
        return str(result)
    except mysql.connector.InterfaceError:
        return "Query executed successfully."
    finally:
        cursor.close()
        conn.close()


@mcp.tool()
def get_hotel_address(hotel_id: int) -> str:
    """Run a SQL query which returns the hotel address, given its ID, on the configured MySQL database from Hotel table."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    query = "SELECT address FROM Hotel WHERE id = %s"
    cursor.execute(query, (hotel_id,))
    try:
        result = cursor.fetchall()
        return str(result)
    except mysql.connector.InterfaceError:
        return "Query executed successfully."
    finally:
        cursor.close()
        conn.close()


@mcp.tool()
def list_tables() -> list:
    """List all tables in the current MySQL database."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return [table[0] for table in tables]


@mcp.tool()
def describe_table(table_name: str) -> list:
    """Describe the structure of a table."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


if __name__ == "__main__":
    mcp.run()
