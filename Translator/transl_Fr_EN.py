from pathlib import Path
from agno.agent import Agent
from mistralai import Mistral
import os
import base64
import asyncio
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.team.team import Team


import base64
import os
from mistralai import Mistral


load_dotenv()

API_MISTRAL= os.getenv("MISTRAL_API")
client = Mistral(api_key=API_MISTRAL)
uploaded_file = client.files.upload(
    file = {
    "file_name": r"D:\Agno\Translator\tarif_6632.pdf",
    "content": open( r"D:\Agno\Translator\tarif_6632.pdf", "rb")
    },
    purpose="ocr"
)
file_url = client.files.get_signed_url(file_id = uploaded_file.id)

response = client.ocr.process(
    model = "mistral-ocr-latest",
    document = {
    "type" : "document_url",
    "document_url" : file_url.url
    },
    include_image_base64=True
    
)

# Save to a file
output_path = r"D:\Agno\Translator\tarif_6632_extracted.md"


def data_uri_to_bytes(data_uri):
    _, encoded = data_uri.split(',', 1)
    return base64.b64decode(encoded)

def export_image(image):
    parsed_image = data_uri_to_bytes(image.image_base64)
    with open(image.id, 'wb') as file:
        file.write(parsed_image)

with open('output.md', 'w') as f:
    for page in response.pages:
        f.write(page.markdown)
        for image in page.images:
            export_image(image)
    

# print(f"Saved all OCR results to {output_path}")

# print("OCR Response:", response.pages[0])