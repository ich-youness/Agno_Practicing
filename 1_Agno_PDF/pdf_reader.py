from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

from dotenv import load_dotenv
import os
from agno.tools.file import FileTools
from pathlib import Path
from pypdf import PdfReader
#l'idee c'est de lire un pdf et l'utiliser comme knowledge base


load_dotenv()
id = os.getenv("id")
api_key=os.getenv("api_key")
id_openai = os.getenv("id_openai")
api_key_openai= os.getenv("api_key_openai")


# pdf = PdfReader(r"D:\Agno\1_Agno_PDF\import morocco.pdf")
# full_text = "" .join(page.extract_text() or "" for page in pdf.pages)

# with open("Read_import_pdf.txt", "w", encoding="utf-8") as file:
#     file.write(full_text)

myAgent = Agent(
    name="PDF reader",
    # model=OpenAIChat(id=id_openai, api_key=api_key_openai),
    model=Gemini(id=id, api_key=api_key),
    tools=[FileTools(Path(r"D:\Agno\1_Agno_PDF\Read_import_pdf.txt"))],
    instructions="""
    you are an expert file reader and content extractor.
    you are able to extract relevant data from the local files.
    you can use the tools you have to read the restrictions and taxes rules in morocco.
    """,
    show_tool_calls=True,

)
myAgent.print_response("what are the taxes rules(VAT) in morocco?")