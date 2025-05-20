#!/usr/bin/env python3
"""
Test script for the MySQL agent.
"""

import asyncio
import time
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from adk.sub_agents.mysql_agent.agent import get_mysql_agent_async

load_dotenv()

async def main():
    """Test the MySQL agent."""
    print("Testing MySQL agent...")

    # Get the MySQL agent
    agent, exit_stack = await get_mysql_agent_async()

    try:
        # Create a session service and session
        session_service = InMemorySessionService()
        session = session_service.create_session(
            state={},
            app_name='mysql_test_app',
            user_id='test_user_id',
        )

        # Create a runner
        runner = Runner(
            app_name='mysql_test',
            agent=agent,
            session_service=session_service,
        )

        # Test listing tables
        print("\nTesting list_tables:")
        await run_test(runner, session, "List all tables in the database")

        # Test dynamic tool (if available)
        print("\nTesting dynamic tool (search-hotel-by-id):")
        await run_test(runner, session, "Search for hotel with ID 1")

        # Test fallback to run_query
        print("\nTesting fallback to run_query:")
        await run_test(runner, session, "Run a query to select the first 5 rows from the Hotel table")

        # Test get_hotel_name
        print("\nTesting get_hotel_name:")
        await run_test(runner, session, "Get the name of hotel with ID 1")
    finally:
        # Clean up resources
        await exit_stack.aclose()

async def run_test(runner, session, query):
    """Run a test query and print the results."""
    content = types.Content(role='user', parts=[types.Part(text=query)])

    start_time = time.time()
    events_async = runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    )

    async for event in events_async:
        if event.is_final_response():
            for p in event.content.parts:
                print(f"Response: {p.text}")
            elapsed_time = time.time() - start_time
            print(f"Time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
