import asyncio
import time

from dotenv import load_dotenv
from google.adk.agents import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import warnings
import logging
from adk.sub_agents.bitbucket_agent import agent as bitbucketAgent
from adk.sub_agents.elasticsearch_agent import agent as elasticSearchAgent
from adk.sub_agents.analyzer_agent import agent as analyzerAgent
from adk.sub_agents.mysql_agent import agent as mysqlAgent


import config

# Ignore all warnings
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
load_dotenv()


async def async_main():
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        app_name='my_app',
        user_id='user_123_session',
    )

    bitbucket_agent, bitbucket_exit_stack = await bitbucketAgent.get_bitbucket_agent_async()
    elasticsearch_agent, elasticsearch_exit_stack = await elasticSearchAgent.get_elasticsearch_agent_async()
    analyzer_agent = analyzerAgent.get_analyzer_agent()

    # mysql agent not used in this example but its working
    mysql_agent, mysql_exit_stack = await mysqlAgent.get_mysql_agent_async()

    try:
        root_agent = SequentialAgent(
            name='manager_assistant',
            description=config.manager_agent_description,
            sub_agents=[elasticsearch_agent, bitbucket_agent, analyzer_agent]
            # sub_agents=[mysql_agent]
        )

        runner = Runner(
            app_name='my_app',
            agent=root_agent,
            session_service=session_service,
        )

        content = types.Content(role='user', parts=[types.Part(text=config.query)])
        #content = types.Content(role='user', parts=[types.Part(text="return hotel name and create data for id = 1 from Hotel table")])

        print("Running agent...")
        start_time = time.time()  #
        events_async = runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content
        )

        async for event in events_async:
            if event.is_final_response():
                for p in event.content.parts:
                    print(f"Event part: {p.text}")
                elapsed_time = time.time() - start_time
                print(f"Time taken for agent to return last event: {elapsed_time:.2f} seconds")

    finally:
        print("Closing MCP server connection...")
        await bitbucket_exit_stack.aclose()
        await elasticsearch_exit_stack.aclose()
        await mysql_exit_stack.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except Exception as e:
        print(f"An error occurred: {e}")
