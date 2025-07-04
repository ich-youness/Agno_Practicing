from letta_client import Letta
from agno.agent import Agent
from agno.tools.telegram import TelegramTools
from agno.models.google import Gemini
import requests
import os
import time
import base64
from dotenv import load_dotenv

def download_telegram_file(token, file_id, save_path):
    file_info = requests.get(f"https://api.telegram.org/bot{token}/getFile", params={"file_id": file_id}).json()
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    response = requests.get(file_url)
    with open(save_path, "wb") as f:
        f.write(response.content)
    return save_path

load_dotenv()
id = os.getenv("id")
api_key = os.getenv("api_key")
LETTA_TOKEN = os.getenv("LETTA_TOKEN")

# === 1. Init Letta agent ===
letta_client = Letta(
    token=LETTA_TOKEN,
    project="default-project",
)
letta_agent_id = os.getenv("LETTA_AGENT_ID")

# === 2. Init Telegram ===
telegram_token = os.getenv("TELEGRAM_TOKEN")
base_url = f"https://api.telegram.org/bot{telegram_token}"
chat_id = "6284042135"

# === 3. Init Agno Agent with Telegram Tool ===
telegram_tool = TelegramTools(token=telegram_token, chat_id=chat_id)
agent = Agent(
    name="telegram",
    model=Gemini(id=id, api_key=api_key),
    tools=[telegram_tool],
    instructions="""
    You are a Telegram bot that sends messages to users.
    Here is the telegram id of the user: 6284042135
    You can use the TelegramTools to send messages to the user.
    """
)

# === 4. Poll Telegram for new messages ===
last_update_id = None

print("🤖 Bot started. Listening to Telegram messages...")

while True:
    try:
        response = requests.get(f"{base_url}/getUpdates", params={"offset": last_update_id, "timeout": 10})
        resp_json = response.json()
        result = resp_json["result"]

        for update in result:
            last_update_id = update["update_id"] + 1
            if "message" in update:
                msg = update["message"]
                user_chat_id = msg["chat"]["id"]

                # === Handle text messages ===
                if "text" in msg:
                    message_text = msg["text"]
                    print(f"👤 User said: {message_text}")
                    letta_msg = {"role": "user", "content": message_text}
                    letta_response = letta_client.agents.messages.create(
                        agent_id=letta_agent_id,
                        messages=[letta_msg],
                    )

                    reply = "Sorry, no response received from Letta."
                    if letta_response.messages:
                        for m in letta_response.messages:
                            if hasattr(m, "content") and m.content:
                                reply = m.content
                                break
                        print(f"🤖 Letta: {reply}")
                    else:
                        print("❌ Letta returned no message.")

                    telegram_tool.send_message(reply)

                # === Handle photo messages ===
                elif "photo" in msg:
                    caption = msg.get("caption", "")
                    photos = msg["photo"]
                    largest_photo = photos[-1]
                    file_id = largest_photo["file_id"]
                    local_path = f"photo_{file_id}.jpg"

                    download_telegram_file(telegram_token, file_id, local_path)
                    print(f"📷 User sent a photo with caption: {caption}")

                    # Step 1: Read and encode the image in base64
                    with open(local_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode("utf-8")
                    


                    # Step 2: Construct Letta message
                    letta_msg = {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    # "type": "base64",
                                    # "media_type": "image/jpeg",
                                    # "data": image_data,
                                    "type": "url",
                                    "url": "https://d9alkaline.com/wp-content/uploads/2025/04/1-Ltr-Bottle.png",
                                },
                            },
                            {
                                "type": "text",
                                "text": caption or "Describe this image."
                            }
                        ],
                    }

                    # Step 3: Send to Letta
                    letta_response = letta_client.agents.messages.create(
                        agent_id=letta_agent_id,
                        messages=[letta_msg],
                    )

                    reply = "Sorry, no response received from Letta."
                    if letta_response.messages:
                        for m in letta_response.messages:
                            if hasattr(m, "content") and m.content:
                                reply = m.content
                                break
                        print(f"🤖 Letta: {reply}")
                    else:
                        print("❌ Letta returned no message.")

                    telegram_tool.send_message(reply)

        time.sleep(2)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)
