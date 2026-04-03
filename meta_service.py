import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")

def enviar_whatsapp(mensaje, numero):
    print("TOKEN cargado:", ACCESS_TOKEN is not None)
    print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("Status:", response.status_code)
    print("Respuesta:", response.text)

    return response.json()