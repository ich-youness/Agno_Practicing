from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

agent = Agent(
  model=Gemini(id="gemini-2.0-flash-exp" , api_key="AIzaSyCc_oV5dIHV_DL-5e-uC48Rym9T5kUn13k"),
  tools=[ReasoningTools(add_instructions=True), YFinanceTools(... )],
  instructions=["Use tables", "Only output the report"],
  markdown=True,
)

agent.print_response("Write a report on gold, give me its latest price", stream=True, show_full_reasoning=True),
