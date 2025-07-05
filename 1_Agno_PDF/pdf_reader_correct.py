from agno.agent import Agent
from agno.models.xai import xAI
from pypdf import PdfReader
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
import os


#l'idee c'est de lire un pdf et l'utiliser comme knowledge base

from agno.knowledge.document import DocumentKnowledgeBase




load_dotenv()
id = os.getenv("id")
api_key=os.getenv("api_key")
id_openai = os.getenv("id_openai")
api_key_openai= os.getenv("api_key_openai")
    
pdf = PdfReader(r"D:\Agno\1_Agno_PDF\pwc-ai-analysis.pdf")

full_text = "" .join(page.extract_text() or "" for page in pdf.pages)
# with open(r"new.txt", "w",  encoding="utf-8") as file:
#     file.write(full_text)

# doc_knowledge = DocumentKnowledgeBase()
# doc_knowledge.add_documents([{
#     "content": full_text,
#     "meta_data": {"source": "pwc-ai-analysis.pdf"}
# }])


def always_return_full_pdf(agent, query, num_documents=None, **kwargs):
    # print(full_text)
    return [{
    "content": full_text,
    "meta_data": {"source": "pwc-ai-analysis.pdf"}
    }]


agent = Agent(
    # model=Gemini(id=id, api_key=api_key),
    model=OpenAIChat(id=id_openai, api_key=api_key_openai), # the openai models works better than the gemini, gemini is not capable of reading the full text, idk if it's a problem with the length of the content or what.
    
    # knowledge=doc_knowledge,

    knowledge=None,
    
    search_knowledge=True,# this is true by default once we set a knowledge base
    retriever=always_return_full_pdf,# gets called everytime we start the agent, for complete control over the knowledge base
    # tools=[always_return_full_pdf]

    instructions=""" you are an expert in ai topics. 
    you get your knowledge only from the pwc-ai-analysis.pdf file.


    """
)

prompt = input("Enter Your Prompt: ")
agent.print_response(prompt)


