from tools import ALL_TOOLS
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import json

load_dotenv()


def init_agent():
    with open("prompts.json", 'r') as f:
        prompts = json.load(f)

    system_prompt = prompts['system_prompt']

    agent = create_agent(
        model="claude-opus-5",
        tools=ALL_TOOLS,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )

    return agent
