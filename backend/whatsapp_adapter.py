# A simple WhatsApp adapter stub. In dev, we just log messages and simulate delivery.
# For production, this will be replaced with a real WhatsApp Business Cloud API client.
from fastapi import HTTPException
import requests
import os

# --- Production WhatsApp Cloud API Configuration ---
# To use the real WhatsApp API, set the following environment variables:
# WHATSAPP_API_KEY: Your WhatsApp Cloud API token
# WHATSAPP_PHONE_NUMBER_ID: The ID of the phone number you are sending from
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_API_URL = f"https://graph.facebook.com/v15.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


class WhatsAppAdapter:
    def __init__(self):
        self.api_key = WHATSAPP_API_KEY
        self.api_url = WHATSAPP_API_URL
        self.is_configured = self.api_key is not None

    def send_text(self, to: str, message: str):
        if not self.is_configured:
            print(f'[WHATSAPP SEND] to={to} message={message}')
            return {'status': 'sent_stub', 'to': to}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        json_data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        # response = requests.post(self.api_url, headers=headers, json=json_data)
        # response.raise_for_status()
        # return response.json()
        print(f"Fake sending to {to}: {message}")
        return {'status': 'sent_stub', 'to': to}


    def send_voice(self, to: str, audio_path: str):
        if not self.is_configured:
            print(f'[WHATSAPP VOICE] to={to} audio={audio_path}')
            return {'status': 'sent_stub', 'to': to}

        # Uploading media and then sending is a two-step process.
        # This is a simplified placeholder.
        print(f"Fake sending voice to {to}: {audio_path}")
        return {'status': 'sent_stub', 'to': to}

# Example usage: adapter = WhatsAppAdapter(); adapter.send_text('+91....', 'Your invoice...')