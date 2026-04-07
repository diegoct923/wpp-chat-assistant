from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from openai_service import interpretar_mensaje, responder_chat
from database import *
import threading
from scheduler import iniciar_scheduler
from meta_service import enviar_whatsapp
from datetime import datetime, timedelta
import pytz

VERIFY_TOKEN = "mi_token_meta_123"

app = FastAPI()

crear_tabla()
crear_tabla_mensajes()
crear_tabla_seguimientos()

# Iniciar el scheduler en un hilo separado
threading.Thread(target=iniciar_scheduler, daemon=True).start()

def armar_respuesta_recordatorio(resultado):
    tarea = resultado.get("tarea") or "Sin texto"
    fecha = resultado.get("fecha")
    hora = resultado.get("hora")
    frecuencia = resultado.get("frecuencia")

    if not fecha:
        fecha = "hoy"
    if not hora:
        hora = "sin hora definida"
    if not frecuencia:
        frecuencia = "solo una vez"

    return (
        "Listo, guardé tu recordatorio ✅\n"
        f"• Tarea: {tarea}\n"
        f"• Fecha: {fecha}\n"
        f"• Hora: {hora}\n"
        f"• Frecuencia: {frecuencia}"
    )

class MensajeEntrada(BaseModel):
    texto: str

@app.get("/")
def inicio():
    return {"mensaje": "Servidor funcionando 🚀"}

@app.post("/mensaje")
def recibir_mensaje(data: MensajeEntrada):
    resultado = interpretar_mensaje(data.texto)

    if resultado.get("tipo") == "recordatorio":
        guardar_recordatorio(resultado)
        return {
            "mensaje_original": data.texto,
            "interpretacion": resultado,
            "status": "guardado correctamente"
        }

    return {
        "mensaje_original": data.texto,
        "interpretacion": resultado
    }

@app.get("/recordatorios")
def ver_recordatorios():
    return obtener_recordatorios()

@app.get("/whatsapp")
def verificar_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge, status_code=200)

    return PlainTextResponse("Token inválido", status_code=403)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # 🔥 1. Ignorar estados (sent, delivered, read)
        if "messages" not in value:
            return PlainTextResponse("ok")

        mensaje = value["messages"][0]["text"]["body"]
        numero = value["messages"][0]["from"]

        print("Mensaje:", mensaje)
        print("Numero:", numero)

        guardar_mensaje(numero, "user", mensaje)

        texto = mensaje.strip().lower().replace(".", "").replace(",", "")

        print("DEBUG TEXTO:", texto)

        # 🔥 2. Manejo de SI / NO (seguimiento)
        if texto in ["si", "sí", "no"]:
            print("ENTRO A SI/NO")
            seguimiento = obtener_ultimo_seguimiento_pendiente(numero)

            if seguimiento:
                seguimiento_id = seguimiento[0]
                recordatorio_id = seguimiento[2]

                if texto in ["si", "sí"]:
                    actualizar_estado_seguimiento(seguimiento_id, "completado")
                    respuesta = "Perfecto ✅ Lo marco como completado."
                else:
                    actualizar_estado_seguimiento(seguimiento_id, "no_completado")

                    recordatorio = obtener_recordatorio_por_id(recordatorio_id)

                    if recordatorio:
                        _, tarea, fecha, hora, frecuencia = recordatorio

                        uruguay = pytz.timezone("America/Montevideo")
                        ahora = datetime.now(uruguay)
                        nueva_hora = (ahora + timedelta(hours=1)).strftime("%H:%M")

                        guardar_recordatorio_manual(
                            usuario=numero,
                            tarea=tarea,
                            fecha="hoy",
                            hora=nueva_hora,
                            frecuencia="solo una vez"
                        )
                        respuesta = f"Entendido. Te lo vuelvo a recordar a las {nueva_hora} ✅"
                    else:
                        respuesta = "Entendido. Lo marco como no completado."

            else:
                respuesta = "No encontré ningún recordatorio pendiente."

            guardar_mensaje(numero, "assistant", respuesta)
            enviar_whatsapp(respuesta, numero)
            return PlainTextResponse("ok")

        # 🔥 3. Detectar recordatorio
        resultado = interpretar_mensaje(mensaje)
        print("Resultado IA:", resultado)

        if resultado.get("tipo") == "recordatorio":
            guardar_recordatorio(resultado, numero)

            respuesta = armar_respuesta_recordatorio(resultado)

            guardar_mensaje(numero, "assistant", respuesta)
            enviar_whatsapp(respuesta, numero)

            return PlainTextResponse("ok")

        # 🔥 4. Chat normal (con poca memoria)
        historial = obtener_mensajes_usuario(numero, limite=6)
        respuesta = responder_chat(mensaje, historial)

        guardar_mensaje(numero, "assistant", respuesta)
        enviar_whatsapp(respuesta, numero)

    except Exception as e:
        print("Error webhook:", e)

    return PlainTextResponse("ok")