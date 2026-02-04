import sys
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Se obtiene la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Se obtiene la ruta de la carpeta padre (backend)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Agregamos 'backend' a los imports de Python
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Cambiamos el directorio de trabajo a 'backend'.
os.chdir(parent_dir)

# Importaciones
try:
    from database import SessionLocal, engine 
    import models
    from scraper_dinamico import buscar_productos_en_web
except ImportError as e:
    print(f" Error crítico de importación: {e}")
    sys.exit(1)

# CONFIGURACIÓN
TOKEN = "8039817548:AAH2ZSJ3aoA05KfOFLLpXDiPGf8M9s_0QOU"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# COMANDOS DEL BOT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el Bot de OfferHunt.\n\n"
        "Comandos:\n"
        "🎯 `/track [producto]` -> Rastrear precio (ej: /track iphone)\n"
        "📋 `/lista` -> Ver rastreos\n"
        "❌ `/borrar` -> Borrar rastreos"
    )

async def track_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    keyword = " ".join(context.args)

    if not keyword:
        await update.message.reply_text("⚠️ Escribe qué buscar. Ej: `/track playstation`")
        return

    db = SessionLocal()
    try:
        db.query(models.PriceAlert).filter(models.PriceAlert.chat_id == chat_id).delete()
        
        alerta = models.PriceAlert(chat_id=chat_id, keyword=keyword)
        db.add(alerta)
        db.commit()
        
        await update.message.reply_text(f"✅ Rastreando: **'{keyword}'**\n🔎 Buscando precios ahora...")
        
        # Marcamos el origen como 'bot' para que no aparezca en el feed principal de la web
        buscar_productos_en_web(keyword, origen="bot")
        
        producto_top = db.query(models.Product)\
            .filter(models.Product.name.ilike(f"%{keyword}%"))\
            .join(models.Price)\
            .order_by(models.Price.amount.asc())\
            .first()

        if producto_top:
            precio = producto_top.prices[-1].amount
            tienda = producto_top.prices[-1].store
            await update.message.reply_text(
                f"🔥 **Mejor precio ahora:**\n"
                f"📦 {producto_top.name}\n"
                f"💰 Gs. {precio:,.0f}\n"
                f"🏪 {tienda}\n"
                f"🔗 {producto_top.url}"
            )
        else:
            await update.message.reply_text("⚠️ No encontré nada aún, seguiré buscando.")

    except Exception as e:
        await update.message.reply_text("❌ Error interno.")
        print(f"Error: {e}")
    finally:
        db.close()

async def list_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    db = SessionLocal()
    alerta = db.query(models.PriceAlert).filter(models.PriceAlert.chat_id == chat_id).first()
    db.close()
    if alerta: await update.message.reply_text(f"👀 Rastreando: **{alerta.keyword}**")
    else: await update.message.reply_text("📭 Nada activo.")

async def delete_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    db = SessionLocal()
    db.query(models.PriceAlert).filter(models.PriceAlert.chat_id == chat_id).delete()
    db.commit()
    db.close()
    await update.message.reply_text("🗑️ Alertas borradas.")

# TAREA AUTOMÁTICA
async def tarea_diaria(application: Application):
    print("⏰ Ejecutando reporte automático...")
    db = SessionLocal()
    try:
        alertas = db.query(models.PriceAlert).all()
        for alerta in alertas:
            print(f"   -> Verificando: {alerta.keyword}")
            
            # --- CAMBIO IMPORTANTE: MARCAMOS EL ORIGEN COMO 'BOT' ---
            buscar_productos_en_web(alerta.keyword, origen="bot")
            
            producto_top = db.query(models.Product)\
                .filter(models.Product.name.ilike(f"%{alerta.keyword}%"))\
                .join(models.Price)\
                .order_by(models.Price.amount.asc())\
                .first()

            if producto_top:
                precio = producto_top.prices[-1].amount
                tienda = producto_top.prices[-1].store
                msg = (
                    f"🌅 **Reporte Diario: {alerta.keyword}**\n"
                    f"📦 {producto_top.name}\n"
                    f"💰 **Gs. {precio:,.0f}**\n"
                    f"🏪 {tienda}\n"
                    f"🔗 {producto_top.url}"
                )
                await application.bot.send_message(chat_id=alerta.chat_id, text=msg)
    except Exception as e:
        print(f"❌ Error tarea: {e}")
    finally:
        db.close()

# INICIALIZADOR DEL SCHEDULER

async def post_init(application: Application):
  
    scheduler = AsyncIOScheduler()
    # Programado cada 60 segundos para pruebas (cambiar a hours=24 en prod)
    scheduler.add_job(tarea_diaria, 'interval', seconds=60, args=[application])
    scheduler.start()
    print("✅ SCHEDULER INICIADO (Modo Demo: 60 seg)")

# Main del Bot

if __name__ == '__main__':
    # Asegurar tablas
    models.Base.metadata.create_all(bind=engine)

    # Construimos el bot y le enganchamos la función post_init
    application = ApplicationBuilder() \
        .token(TOKEN) \
        .post_init(post_init) \
        .build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('track', track_product))
    application.add_handler(CommandHandler('lista', list_alerts))
    application.add_handler(CommandHandler('borrar', delete_alerts))

    print("🤖 BOT DE OFFERHUNT INICIADO.")
    application.run_polling()