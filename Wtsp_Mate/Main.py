from letta_client import Letta, MessageCreate
from agno.tools.telegram import TelegramTools
import requests
import os
import time
from dotenv import load_dotenv

import requests

def download_telegram_file(token, file_id, save_path):
    # Get file path from Telegram
    file_info = requests.get(f"https://api.telegram.org/bot{token}/getFile", params={"file_id": file_id}).json()
    file_path = file_info["result"]["file_path"]
    # Download the file
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    response = requests.get(file_url)
    with open(save_path, "wb") as f:
        f.write(response.content)
    return save_path

# Load environment variables
load_dotenv()

# === 1. Telegram and Letta Configuration ===
telegram_token = os.getenv("TELEGRAM_TOKEN")
base_url = f"https://api.telegram.org/bot{telegram_token}"
chat_id = "6284042135"  # Your chat ID
LETTA_TOKEN= os.getenv("LETTA_TOKEN")
letta_client = Letta(
    token=LETTA_TOKEN,
    project="default-project",
)
letta_agent_id = os.getenv("LETTA_AGENT_ID")

# === 2. Initialize Letta Client ===
# letta_client = Letta(token=letta_token, project=letta_project)

# === 3. Initialize Telegram Tool ===
telegram_tool = TelegramTools(token=telegram_token, chat_id=chat_id)

# === 4. Poll Telegram for New Messages ===
last_update_id = None

print("🤖 Bot started. Listening to Telegram messages...")

while True:
    try:
        # Get latest updates from Telegram
        response = requests.get(f"{base_url}/getUpdates", params={"offset": last_update_id, "timeout": 10})
        resp_json = response.json()

        if not resp_json.get("ok"):
            print(f"⚠️ Telegram API error: {resp_json.get('description', 'Unknown error')}")
            time.sleep(5)
            continue

        result = resp_json["result"]

        for update in result:
            last_update_id = update["update_id"] + 1  # Prevent duplicate messages

            # Extract message content
            if "message" in update:
                msg = update["message"]
                user_chat_id = msg["chat"]["id"]

                # Handle text messages
                if "text" in msg:
                    message_text = msg["text"]
                    print(f"👤 User said: {message_text}")
                    letta_msg = MessageCreate(role="user", content=message_text)
                    letta_response = letta_client.agents.messages.create(
                        agent_id=letta_agent_id,
                        messages=[letta_msg],
                    )

                    # Get Letta's reply
                    reply = "Sorry, no response received from Letta."
                    if letta_response.messages:
                        for msg in letta_response.messages:
                            if hasattr(msg, "content") and msg.content:
                                reply = msg.content
                                break
                        print(f"🤖 Letta: {reply}")
                    else:
                        print("❌ Letta returned no message.")

                    # Send reply back to Telegram
                    telegram_tool.send_message(reply)
                elif "photo" in msg:
                    caption = msg.get("caption", "")
                    photos = msg["photo"]
                    largest_photo = photos[-1]  # Last is largest
                    file_id = largest_photo["file_id"]
                    local_path = f"photo_{file_id}.jpg"
                    download_telegram_file(telegram_token, file_id, local_path)
                    print(f"📷 User sent a photo with caption: {caption}")

                    # Send caption to Letta (optionally, you can also send info about the photo)
                    letta_msg = MessageCreate(role="user", content=f"[Photo received] {caption}")
                    letta_response = letta_client.agents.messages.create(
                        agent_id=letta_agent_id,
                        messages=[letta_msg],
                    )
                     # Get Letta's reply
                    reply = "Sorry, no response received from Letta."
                    if letta_response.messages:
                        for msg in letta_response.messages:
                            if hasattr(msg, "content") and msg.content:
                                reply = msg.content
                                break
                        print(f"🤖 Letta: {reply}")
                    else:
                        print("❌ Letta returned no message.")

                    # Send reply back to Telegram
                    telegram_tool.send_message(reply)


        time.sleep(2)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)