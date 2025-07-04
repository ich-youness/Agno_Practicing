from agno.agent import Agent
from mistralai import Mistral
import os
import base64
import asyncio
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.team.team import Team

load_dotenv()
id = os.getenv("id")
api_key = os.getenv("api_key")
API_MISTRAL= os.getenv("MISTRAL_API")

def encode_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

class TranslationTool:
    def run(self, path: str) -> str:
        client = Mistral(api_key=API_MISTRAL)
        base64_pdf = encode_pdf(path)
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}"
            },
            include_image_base64=False
        )
        return ocr_response["text"]

# Agent that uses the tool


translation_agent = Agent(
    name="Translation Agent",
    role="Translate Moroccan law from French to English",
    # model=OpenAIChat("gpt-4o"),
    model=Gemini(id=id, api_key=api_key),
    tools=[TranslationTool()],
    
    add_name_to_instructions=True,
    instructions="""
        You are responsible for translating Moroccan import laws from French into English.
        here is the link of the document: 'D:\Agno\Translator\tarif_6632.pdf'
        Use the OCR output and summarize the most relevant legal sections related to:
        - Customs Duties
        - VAT
        - Product Category Restrictions
        - Required documents or certifications
    """,
)

restriction_agent = Agent(
    name="Restriction Agent",
    role="Extract any product or shipping restrictions",
    # model=OpenAIChat("gpt-4o"),
    model=Gemini(id=id, api_key=api_key),
    add_name_to_instructions=True,
    instructions="""
        You are responsible for identifying restrictions in the UK export and Moroccan import laws.
        Based on the product details (type, raw materials, quantity), answer:
        - Is the product restricted or controlled?
        - Are there limits based on quantity?
        - Are any special licenses required?
    """,
)
tax_agent = Agent(
    name="Tax Agent",
    role="Extract and calculate taxes and fees",
    # model=OpenAIChat("gpt-4o"),
    model=Gemini(id=id, api_key=api_key),
    add_name_to_instructions=True,
    instructions="""
        Your job is to extract applicable taxes from both UK and Moroccan documents.
        Then calculate the taxes based on the product’s declared value.
        Show results in a table including:
        - Export License Fees (UK)
        - Exit Duty (UK)
        - Import VAT (Morocco)
        - Customs Duty (Morocco)
    """,
)
report_agent = Agent(
    name="Report Generator Agent",
    role="Generate a clean report with tables",
    # model=OpenAIChat("gpt-4o"),
    model=Gemini(id=id, api_key=api_key),
    add_name_to_instructions=True,
    instructions="""
        Format the final result into a clean, professional report.
        Sections:
        1. Product Summary
        2. Restrictions
        3. Tax Summary Table
        4. Total Estimated Cost
        Use Markdown formatting for tables and headings.
    """,
)



compliance_team = Team(
    name="Export Compliance Team",
    mode="collaborate",
    # model=OpenAIChat("gpt-4o"),
    model=Gemini(id=id, api_key=api_key),
    members=[
        translation_agent,
        restriction_agent,
        tax_agent,
        report_agent
    ],
    instructions=[
        "You're a team responsible for estimating export cost and compliance for a UK manufacturer shipping to Morocco.",
        "First translate the Moroccan law, then identify restrictions, taxes, and summarize it all.",
    ],
    success_criteria="Return a complete cost and compliance report.",
    enable_agentic_context=True,
    show_tool_calls=True,
    show_members_responses=True,
    markdown=True,
    debug_mode=True,
)


if __name__ == "__main__":
    asyncio.run(
        compliance_team.print_response(
            message="Generate a compliance report for a UK company shipping 500 Bluetooth trackers to Morocco. Use the provided UK export and Moroccan import PDFs.",
            stream=True,
            stream_intermediate_steps=True,
        )
    )
