from agno.agent import Agent
from mistralai import Mistral
import base64
import os
from dotenv import load_dotenv
from agno.models.google import Gemini


load_dotenv()
id = os.getenv("id")
api_key = os.getenv("api_key")
API_MISTRAL= os.getenv("MISTRAL_API")
# OCR extraction tool logic
def mistral_ocr_extract(pdf_path: str, output_md_path: str = "output.md"):
    
    client = Mistral(api_key=API_MISTRAL)

    # Upload and get file URL
    with open(pdf_path, "rb") as f:
        uploaded = client.files.upload(
            file={"file_name": os.path.basename(pdf_path), "content": f},
            purpose="ocr"
        )

    signed_url = client.files.get_signed_url(file_id=uploaded.id)

    # OCR Process
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": signed_url.url},
        include_image_base64=True
    )

    # Save text and images
    def data_uri_to_bytes(data_uri):
        _, encoded = data_uri.split(",", 1)
        return base64.b64decode(encoded)

    def export_image(image):
        with open(image.id, 'wb') as file:
            file.write(data_uri_to_bytes(image.image_base64))

    with open(output_md_path, 'w', encoding='utf-8') as f:
        for page in response.pages:
            f.write(page.markdown)
            for image in page.images:
                export_image(image)

    return f"OCR complete. Extracted text saved to: {output_md_path}"

# Define the OCR agent
ocr_agent = Agent(
    name="OCR Extractor Agent",
    instructions="""
    You are an OCR extraction agent that processes PDF documents to extract text and images.
    Use the Mistral OCR tool to extract text from legal documents and save it as a .md file.
    The output should be a Markdown file containing the extracted text and images.
    here are the 2 files you should be extracting:  D:\Agno\Translator\export UK.pdf and D:\Agno\Translator\import morocco.pdf
        """,
    model=Gemini(id=id, api_key=api_key),
    tools=[mistral_ocr_extract]
)
 
ocr_agent.print_response(
    "Extract text from the two legal document PDF using Mistral OCR and save it as a .md file.", stream=True
)


def read_text() -> str:
    
      
    with open("D:\Agno\Translator\import_morocco.md", "r", encoding="utf-8") as file:
        return file.read()
    

translation_agent = Agent(
    name="Markdown Translator Agent",
    instructions="""
    You are a professional translator. Translate the provided Markdown content from French to English.
    Only output the translated English Markdown text.
    here is the file you should be translating: D:\Agno\Translator\import_morocco.md
    save the translated content to a file named D:/Agno/Translator/translated_output.md
    """,
    save_response_to_file=True,
    # save_path="D:/Agno/Translator/translated_output.md",
    model=Gemini(id=id, api_key=api_key),
    tools=[read_text()],
)

# translation_agent.print_response("Translate this file D:\Agno\Translator\import_morocco.md from French to English.")