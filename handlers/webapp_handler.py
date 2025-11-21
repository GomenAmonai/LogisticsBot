import logging
import json
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import Database
from models.user import UserRole
from config import WEBAPP_URL

logger = logging.getLogger(__name__)
db = Database()


async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик данных из WebApp"""
    if not update.message or not update.message.web_app_data:
        return
    
    user_id = update.effective_user.id
    data = update.message.web_app_data.data
    
    try:
        data_dict = json.loads(data)
        action = data_dict.get('action')
        
        if action == 'create_order':
            description = data_dict.get('description', '')
            if description:
                order_id = db.create_order(
                    client_id=user_id,
                    description=description,
                    from_address=data_dict.get('from_address'),
                    to_address=data_dict.get('to_address'),
                    from_contact=data_dict.get('from_contact'),
                    to_contact=data_dict.get('to_contact'),
                    weight=float(data_dict.get('weight', 0)),
                    price=float(data_dict.get('price', 0))
                )
                
                # Получаем информацию о заказе
                order = db.get_order(order_id)
                tracking_number = order.get('tracking_number', 'N/A')
                
                await update.message.reply_text(
                    f"✅ Заказ #{order_id} успешно создан!\n\n"
                    f"📦 Описание: {description}\n"
                    f"🔢 Номер отслеживания: {tracking_number}\n"
                    f"📍 От: {data_dict.get('from_address', 'Не указано')}\n"
                    f"📍 Куда: {data_dict.get('to_address', 'Не указано')}\n"
                    f"💰 Цена: {data_dict.get('price', 0)} ₽\n\n"
                    f"Статус: ⏳ Ожидает обработки"
                )
            else:
                await update.message.reply_text("❌ Описание заказа не может быть пустым")
        
        elif action == 'test':
            await update.message.reply_text("✅ Данные получены из WebApp!")
        
        else:
            await update.message.reply_text(f"Получено действие: {action}")
    
    except json.JSONDecodeError:
        logger.error(f"Ошибка парсинга JSON из WebApp: {data}")
        await update.message.reply_text("❌ Ошибка обработки данных")
    except Exception as e:
        logger.error(f"Ошибка обработки WebApp данных: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке данных")


def register_webapp_handlers(application):
    """Регистрирует обработчики для WebApp"""
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data_handler)
    )

