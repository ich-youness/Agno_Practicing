from agno.agent import Agent


from agno.models.google import Gemini
from dotenv import load_dotenv
import os

load_dotenv()
id = os.getenv("id")
api_key = os.getenv("api_key")

task = (
    "research the situation in the world right now."
    "predict how it will be in the next 10 years."
    "what will be the big improvements."
)

reasoning_agent = Agent(
    model=Gemini(id=id, api_key=api_key),
    reasoning=False,
    markdown=True,
)
reasoning_agent.print_response(task, stream=True, show_full_reasoning=True)