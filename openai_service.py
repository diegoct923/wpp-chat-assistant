from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpretar_mensaje(texto: str):
    prompt = f"""
Sos un sistema que interpreta mensajes de usuarios para crear recordatorios.

Tu tarea es analizar el mensaje y devolver SOLO un JSON válido.
No expliques nada.
No hables como asistente.
No agregues texto fuera del JSON.

Si el mensaje es un recordatorio, devolver este formato:
{{
  "tipo": "recordatorio",
  "tarea": "texto de la tarea",
  "fecha": null,
  "hora": "HH:MM" o null,
  "frecuencia": "diaria" o null
}}

Si no es un recordatorio, devolver:
{{
  "tipo": "otro"
}}

Mensaje del usuario:
"{texto}"
"""

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        if response.output:
            for item in response.output:
                if hasattr(item, "content") and item.content:
                    for c in item.content:
                        if hasattr(c, "text") and c.text:
                            texto_json = c.text
                            return json.loads(texto_json)

        return {"error": "Respuesta vacía de OpenAI"}

    except json.JSONDecodeError:
        return {
            "error": "La respuesta no vino en JSON válido"
        }

    except Exception as e:
        return {
            "error": "OpenAI falló",
            "detalle": str(e)
        }
    
def responder_chat(texto: str, historial=None):
    if historial is None:
        historial = []

    mensajes = [
        {
            "role": "system",
            "content": "Sos un asistente útil que responde por WhatsApp. Respondé de forma clara, corta, natural y con memoria de la conversación. No uses markdown raro ni respuestas demasiado largas."
        }
    ]

    for mensaje in historial:
        mensajes.append({
            "role": mensaje["role"],
            "content": mensaje["content"]
        })

    mensajes.append({
        "role": "user",
        "content": texto
    })

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=mensajes
        )

        if response.output:
            for item in response.output:
                if hasattr(item, "content") and item.content:
                    for c in item.content:
                        if hasattr(c, "text") and c.text:
                            return c.text

        return "No pude responder en este momento."

    except Exception as e:
        return f"Hubo un error respondiendo: {str(e)}"