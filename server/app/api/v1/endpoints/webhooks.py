import requests
import os
from fastapi import APIRouter, Request

router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@router.post("/telegram")
async def telegram_webhook(request: Request):
    body = await request.json()
    if "message" in body:
        chat_id = body["message"]["chat"]["id"]
        text = body["message"]["text"]

        # Call chat engine endpoint
        try:
            response = requests.post(
                "https://civi-backend-app-dtfsb2bvdua8epax.eastus2-01.azurewebsites.net/api/v1/chat/message",
                json={"content": text, "conversation_id": chat_id},
                timeout=15  
            )
            if response.status_code == 200:
                reply = response.json().get("content", "No response from the AI engine")
            else:
                reply = "Sorry, there was an error contacting the chat"
        except Exception as e:
            reply = "A technical error occurred"
        # Send the reply back to Telegram
        send_telegram_message(chat_id, reply)

    return {"ok": True}
