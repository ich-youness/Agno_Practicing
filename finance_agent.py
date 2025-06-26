from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

from dotenv import load_dotenv
import os

load_dotenv()  

id = os.getenv("id")
api_key = os.getenv("api_key")

finance_agent = Agent(
    model=Gemini(id=id , api_key=api_key),
    tools=[
        YFinanceTools(
            stock_price=True,

            analyst_recommendations=True,
            stock_fundamentals=True,
            historical_prices=True,
            company_info=True,
            company_news=True,
        )
    ],
    instructions=dedent("""\
        You are a seasoned Wall Street analyst with deep expertise in market analysis! 📊

 
    """),
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
)

# Example usage with detailed market analysis request
finance_agent.print_response(
    "What's the latest news and financial performance of NAS?", stream=True
)

# Semiconductor market analysis example
# finance_agent.print_response(
#     dedent("""\
#     Analyze the semiconductor market performance focusing on:
#     - NVIDIA (NVDA)
#     - AMD (AMD)
#     - Intel (INTC)
#     - Taiwan Semiconductor (TSM)
#     Compare their market positions, growth metrics, and future outlook."""),
#     stream=True,
# )

# # Automotive market analysis example
# finance_agent.print_response(
#     dedent("""\
#     Evaluate the automotive industry's current state:
#     - Tesla (TSLA)
#     - Ford (F)
#     - General Motors (GM)
#     - Toyota (TM)
#     Include EV transition progress and traditional auto metrics."""),
#     stream=True,
# )

# # More example prompts to explore:
# """
# Advanced analysis queries:
# 1. "Compare Tesla's valuation metrics with traditional automakers"
# 2. "Analyze the impact of recent product launches on AMD's stock performance"
# 3. "How do Meta's financial metrics compare to its social media peers?"
# 4. "Evaluate Netflix's subscriber growth impact on financial metrics"
# 5. "Break down Amazon's revenue streams and segment performance"

# Industry-specific analyses:
# Semiconductor Market:
# 1. "How is the chip shortage affecting TSMC's market position?"
# 2. "Compare NVIDIA's AI chip revenue growth with competitors"
# 3. "Analyze Intel's foundry strategy impact on stock performance"
# 4. "Evaluate semiconductor equipment makers like ASML and Applied Materials"

# Automotive Industry:
# 1. "Compare EV manufacturers' production metrics and margins"
# 2. "Analyze traditional automakers' EV transition progress"
# 3. "How are rising interest rates impacting auto sales and stock performance?"
# 4. "Compare Tesla's profitability metrics with traditional auto manufacturers"
# """