from zoneinfo import ZoneInfo

import schedule
import time
from datetime import datetime
from database import obtener_recordatorios, guardar_seguimiento
from meta_service import enviar_whatsapp

enviados = set()

def revisar_recordatorios():
    ahora_dt = datetime.now(ZoneInfo("America/Montevideo"))
    ahora = ahora_dt.strftime("%Y-%m-%d %H:%M")
    hora_actual = ahora_dt.strftime("%H:%M")

    print("Revisando recordatorios a las:", ahora)

    try:
        recordatorios = obtener_recordatorios()

        for r in recordatorios:
            id, usuario, tarea, fecha, hora, frecuencia = r

            clave_envio = f"{id}-{ahora}"

            if hora == hora_actual and clave_envio not in enviados:
                print(f"Coincidió la hora para id={id}")

                try:
                    mensaje = f"🔔 Recordatorio: {tarea}\n¿Ya lo hiciste? (si/no)"
                    resultado = enviar_whatsapp(mensaje, usuario)
                    print("WhatsApp enviado:", resultado)

                    fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    guardar_seguimiento(usuario, id, "pendiente", fecha_envio)

                    enviados.add(clave_envio)

                except Exception as e:
                    print("Error enviando WhatsApp:", e)

    except Exception as e:
        print("Error revisando recordatorios:", e)

def iniciar_scheduler():
    schedule.every(10).seconds.do(revisar_recordatorios)

    while True:
        schedule.run_pending()
        time.sleep(1)