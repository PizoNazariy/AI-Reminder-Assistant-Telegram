import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
logging.basicConfig(level=logging.INFO)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ARCHIVO = "recordatorios.json"

# ── JSON: funciones de datos ───────────────────────────────
def cargar():
    if not Path(ARCHIVO).exists():
        return []
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar(datos):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def guardar_recordatorio(chat_id, mensaje, fecha_iso):
    datos = cargar()
    datos.append({
        "id": int(datetime.now().timestamp() * 1000),
        "chat_id": chat_id,
        "mensaje": mensaje,
        "fecha": fecha_iso,
        "enviado": False,
        "fecha_enviado": None
    })
    guardar(datos)

def obtener_pendientes():
    ahora = datetime.now().isoformat()
    return [r for r in cargar() if r["fecha"] <= ahora and not r["enviado"]]

def marcar_enviado(id):
    datos = cargar()
    for r in datos:
        if r["id"] == id:
            r["enviado"] = True
            r["fecha_enviado"] = datetime.now().isoformat()
    guardar(datos)

def limpiar_antiguos():
    datos = cargar()
    limite = (datetime.now() - timedelta(days=10)).isoformat()
    antes = len(datos)
    datos = [r for r in datos if not (r["enviado"] and r.get("fecha_enviado", "") <= limite)]
    despues = len(datos)
    guardar(datos)
    if antes != despues:
        logging.info(f"🧹 Limpieza automática: {antes - despues} recordatorios eliminados")

# ── Groq: interpretar mensaje ──────────────────────────────
def interpretar_con_groq(texto: str, recordatorios_pendientes: list) -> dict:
    ahora = datetime.now().isoformat()
    lista_recordatorios = "\n".join(
        [f"- ID {r['id']}: {r['mensaje']} ({r['fecha']})" for r in recordatorios_pendientes]
    ) or "No hay recordatorios pendientes."

    prompt = f"""Hoy es {ahora}.
El usuario dice: "{texto}"

Recordatorios pendientes del usuario:
{lista_recordatorios}

Responde SOLO con uno de estos JSON:

Si quiere AÑADIR un recordatorio:
{{"intencion": "añadir", "mensaje": "texto breve", "fecha_iso": "YYYY-MM-DDTHH:MM:SS"}}

Si quiere BORRAR un recordatorio (busca el más parecido a lo que dice):
{{"intencion": "borrar", "id": 1234567890}}

Si quiere VER o LISTAR sus recordatorios:
{{"intencion": "listar"}}

Si es otra cosa:
{{"intencion": "otro", "respuesta": "mensaje amigable en el mismo idioma"}}"""

    respuesta = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    contenido = respuesta.choices[0].message.content.strip()
    contenido = contenido.replace("```json", "").replace("```", "").strip()
    return json.loads(contenido)

# ── Handlers de Telegram ───────────────────────────────────
async def handle_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    chat_id = str(update.effective_chat.id)


    try:
        datos = cargar()
        pendientes = [r for r in datos if r["chat_id"] == chat_id and not r["enviado"]]
        resultado = interpretar_con_groq(texto, pendientes)

        if resultado["intencion"] == "añadir":
            guardar_recordatorio(chat_id, resultado["mensaje"], resultado["fecha_iso"])
            fecha_legible = datetime.fromisoformat(resultado["fecha_iso"]).strftime("%d/%m/%Y a las %H:%M")
            await update.message.reply_text(
                f"✅ Recordatorio guardado para el {fecha_legible}\n📌 {resultado['mensaje']}"
            )

        elif resultado["intencion"] == "borrar":
            datos = cargar()
            datos_filtrados = [r for r in datos if r["id"] != resultado["id"]]
            if len(datos_filtrados) == len(datos):
                await update.message.reply_text("❌ No encontré ese recordatorio.")
            else:
                guardar(datos_filtrados)
                await update.message.reply_text("🗑️ Recordatorio borrado.")

        elif resultado["intencion"] == "listar":
            if not pendientes:
                await update.message.reply_text("📭 No tienes recordatorios pendientes.")
            else:
                pendientes.sort(key=lambda r: r["fecha"])
                lineas = ["📋 *Tus recordatorios pendientes:*\n"]
                for r in pendientes:
                    fecha_legible = datetime.fromisoformat(r["fecha"]).strftime("%d/%m/%Y %H:%M")
                    lineas.append(f"⏳ {fecha_legible} — {r['mensaje']}")
                await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

        else:
            await update.message.reply_text(resultado["respuesta"])

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ No entendí bien. Prueba con: 'Recuérdame llamar al médico mañana a las 10'")

async def cmd_lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    datos = cargar()
    pendientes = [r for r in datos if r["chat_id"] == chat_id and not r["enviado"]]
    pendientes.sort(key=lambda r: r["fecha"])

    if not pendientes:
        await update.message.reply_text("📭 No tienes recordatorios pendientes.")
        return

    lineas = ["📋 *Tus recordatorios pendientes:*\n"]
    for r in pendientes:
        fecha_legible = datetime.fromisoformat(r["fecha"]).strftime("%d/%m/%Y %H:%M")
        lineas.append(f"⏳ {fecha_legible} — {r['mensaje']}")

    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    datos = cargar()
    mis_recordatorios = [r for r in datos if r["chat_id"] == chat_id]
    mis_recordatorios.sort(key=lambda r: r["fecha"])

    if not mis_recordatorios:
        await update.message.reply_text("📭 No tienes ningún recordatorio.")
        return

    lineas = ["📋 *Todos tus recordatorios:*\n"]
    for r in mis_recordatorios:
        fecha_legible = datetime.fromisoformat(r["fecha"]).strftime("%d/%m/%Y %H:%M")
        estado = "✅" if r["enviado"] else "⏳"
        lineas.append(f"{estado} {fecha_legible} — {r['mensaje']}")

    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente de recordatorios.\n\n"
        "Puedes hablarme con naturalidad:\n"
        "• _'Recuérdame tomar la medicación mañana a las 9'_\n"
        "• _'Avísame el viernes a las 18h que tengo reunión'_\n"
        "• _'Borra el recordatorio del médico'_\n"
        "• _'Muéstrame mis recordatorios'_\n\n"
        "O usa los comandos:\n"
        "/lista — recordatorios pendientes\n"
        "/todos — todos incluidos los completados",
        parse_mode="Markdown"
    )

# ── Scheduler ─────────────────────────────────────────────
async def revisar_recordatorios(app):
    for r in obtener_pendientes():
        try:
            await app.bot.send_message(
                chat_id=r["chat_id"],
                text=f"⏰ *Recordatorio:* {r['mensaje']}",
                parse_mode="Markdown"
            )
            marcar_enviado(r["id"])
            logging.info(f"Recordatorio {r['id']} enviado")
        except Exception as e:
            logging.error(f"Error enviando recordatorio {r['id']}: {e}")

async def revisar_limpieza():
    limpiar_antiguos()

# ── Main ───────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("lista", cmd_lista))
    app.add_handler(CommandHandler("todos", cmd_todos))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_texto))

    async def post_init(application):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(revisar_recordatorios, "interval", seconds=60, args=[application])
        scheduler.add_job(revisar_limpieza, "cron", hour=3, minute=0)
        scheduler.start()
        logging.info("✅ Scheduler iniciado")

    app.post_init = post_init

    logging.info("✅ Bot iniciado correctamente")
    app.run_polling()

if __name__ == "__main__":
    main()
