"""
Dynamic MySQL Tool Generator.

This module provides functionality to generate dynamic MySQL MCP tools based on YAML configurations.
"""

import os
import tempfile
import logging
from typing import List, Dict, Any

from adk.tools.mysql_tool.models import ToolConfig

logger = logging.getLogger(__name__)

class DynamicMySQLMCPGenerator:
    """Generates a dynamic MySQL MCP server script based on tool configurations."""

    @staticmethod
    def generate_mcp_script(tools: List[ToolConfig]) -> str:
        """
        Generate a MySQL MCP server script for the given tools.

        Args:
            tools: List of tool configurations

        Returns:
            A string containing the Python script for the MCP server
        """
        script = """#!/usr/bin/env python3
\"\"\"
Dynamically generated MySQL MCP Tool: FastMCP server exposing MySQL-related tools.
\"\"\"

import os
import mysql.connector
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="DynamicMySQLServer")

def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT")),
    )

"""

        # Add the standard run_query tool
        script += """
@mcp.tool()
def run_query(query: str) -> str:
    \"\"\"Run a SQL query on the configured MySQL database.\"\"\"
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

"""

        # Add dynamic tools based on configuration
        for tool in tools:
            if tool.kind == 'mysql-sql':
                # Create function name from tool name
                func_name = tool.name.replace('-', '_')

                # Build parameter list
                params_code = []
                param_names = []
                for param in tool.parameters:
                    param_name = param.get('name')
                    param_type = param.get('type', 'str')

                    # Ensure parameter type is a valid Python type
                    valid_types = {'str', 'int', 'float', 'bool', 'dict', 'list'}
                    if param_type not in valid_types:
                        logger.warning(f"Invalid parameter type '{param_type}' for parameter '{param_name}'. Using 'str' instead.")
                        param_type = 'str'

                    params_code.append(f"{param_name}: {param_type}")
                    param_names.append(param_name)

                params_str = ", ".join(params_code)

                # Build SQL statement with parameter substitution
                sql_statement = tool.statement

                # Replace $1, $2, etc. with %s for MySQL
                for i in range(len(param_names), 0, -1):
                    sql_statement = sql_statement.replace(f"${i}", "%s")

                # Create the function
                script += f"""
@mcp.tool()
def {func_name}({params_str}) -> str:
    \"\"\"{tool.description}\"\"\"
    conn = get_mysql_connection()
    cursor = conn.cursor()

    # Prepare the SQL statement with parameters
    query = \"\"\"{sql_statement}\"\"\"

"""

                # Add parameter handling based on the number of parameters
                if param_names:
                    params_tuple = ", ".join(param_names)
                    if len(param_names) == 1:
                        # For a single parameter, we need to make it a tuple with a trailing comma
                        script += f"    cursor.execute(query, ({params_tuple},))\n"
                    else:
                        script += f"    cursor.execute(query, ({params_tuple}))\n"
                else:
                    script += "    cursor.execute(query)\n"

                script += """
    try:
        result = cursor.fetchall()
        return str(result)
    except mysql.connector.InterfaceError:
        return "Query executed successfully."
    finally:
        cursor.close()
        conn.close()

"""

        # Add the main block
        script += """
if __name__ == "__main__":
    mcp.run()
"""

        return script

    @staticmethod
    def create_temp_script_file(tools: List[ToolConfig]) -> str:
        """
        Create a temporary file with the generated MCP script.

        Args:
            tools: List of tool configurations

        Returns:
            Path to the temporary script file
        """
        script_content = DynamicMySQLMCPGenerator.generate_mcp_script(tools)

        # Create a temporary file for the script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name

        logger.info(f"Created dynamic MySQL MCP script at {script_path}")
        return script_path
