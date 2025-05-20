from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

import config


def get_analyzer_agent():
    root_agent = Agent(
        model=LiteLlm(model=config.model),
        name='analyzer_assistant',
        description=config.analyzer_agent_description,
        instruction=config.analyzer_agent_instruction,
    )

    return root_agent