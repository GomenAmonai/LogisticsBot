"""
Модуль для отправки логов и уведомлений в Telegram группу
"""
import logging
import traceback
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

# ID группы для логов (устанавливается через .env)
LOG_GROUP_ID = None

# Инициализация бота для отправки сообщений
_bot_instance = None


def init_log_group(group_id: str = None):
    """Инициализирует ID группы для логов"""
    global LOG_GROUP_ID
    if group_id:
        LOG_GROUP_ID = int(group_id) if group_id.isdigit() or (group_id.startswith('-') and group_id[1:].isdigit()) else None
    return LOG_GROUP_ID is not None


async def _get_bot():
    """Получает экземпляр бота для отправки сообщений"""
    global _bot_instance
    if _bot_instance is None and BOT_TOKEN:
        _bot_instance = Bot(token=BOT_TOKEN)
    return _bot_instance


async def send_to_group(message: str, parse_mode: str = None):
    """Отправляет сообщение в группу логов"""
    if not LOG_GROUP_ID:
        return False
    
    try:
        bot = await _get_bot()
        if bot:
            await bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=message,
                parse_mode=parse_mode
            )
            return True
    except TelegramError as e:
        error_msg = str(e)
        logger.error(f"Ошибка отправки в группу: {e}")
        
        # Обрабатываем миграцию группы в супергруппу
        if "migrated" in error_msg.lower() or "new chat id" in error_msg.lower():
            # Пытаемся извлечь новый ID из сообщения об ошибке
            import re
            match = re.search(r'-?\d+', error_msg)
            if match:
                new_id = match.group()
                logger.warning(f"⚠️ Группа мигрирована! Новый ID: {new_id}. Обновите LOG_GROUP_ID в .env")
                # Можно автоматически обновить, но лучше вручную
                # global LOG_GROUP_ID
                # LOG_GROUP_ID = int(new_id)
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке в группу: {e}")
    
    return False


def send_log_sync(message: str, parse_mode: str = None):
    """Синхронная обертка для отправки в группу"""
    import threading
    
    def send_in_thread():
        """Отправка в отдельном потоке с новым event loop"""
        try:
            asyncio.run(send_to_group(message, parse_mode))
        except Exception as e:
            logger.error(f"Ошибка отправки в потоке: {e}")
    
    try:
        # Пытаемся использовать существующий event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если цикл запущен, отправляем в отдельном потоке
                thread = threading.Thread(target=send_in_thread, daemon=True)
                thread.start()
                return True
            else:
                # Цикл существует, но не запущен
                loop.run_until_complete(send_to_group(message, parse_mode))
                return True
        except RuntimeError:
            # Нет event loop, создаем новый
            asyncio.run(send_to_group(message, parse_mode))
            return True
    except Exception as e:
        logger.error(f"Ошибка в send_log_sync: {e}", exc_info=True)
        # Пробуем в отдельном потоке как fallback
        try:
            thread = threading.Thread(target=send_in_thread, daemon=True)
            thread.start()
            return True
        except Exception as e2:
            logger.error(f"Критическая ошибка отправки: {e2}")
            return False


def format_error_log(error: Exception, context: str = None):
    """Форматирует ошибку для отправки в группу"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"🚨 <b>ОШИБКА</b>\n"
    message += f"⏰ {timestamp}\n\n"
    
    if context:
        message += f"📍 <b>Контекст:</b> {context}\n\n"
    
    message += f"❌ <b>Тип:</b> {type(error).__name__}\n"
    message += f"💬 <b>Сообщение:</b> {str(error)}\n\n"
    
    # Добавляем traceback (первые 10 строк)
    tb_lines = traceback.format_exc().split('\n')[:10]
    if tb_lines:
        tb_text = '\n'.join(tb_lines)
        message += f"📋 <b>Traceback:</b>\n<code>{tb_text}</code>"
    
    return message


def format_api_log(method: str, path: str, status: int, duration: float, user_id: int = None):
    """Форматирует API запрос для отправки в группу"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Определяем эмодзи по статусу
    if status >= 500:
        emoji = "🔴"
    elif status >= 400:
        emoji = "🟡"
    else:
        emoji = "🟢"
    
    message = f"{emoji} <b>API Request</b>\n"
    message += f"⏰ {timestamp}\n\n"
    message += f"🔹 <b>Method:</b> {method}\n"
    message += f"🔹 <b>Path:</b> {path}\n"
    message += f"🔹 <b>Status:</b> {status}\n"
    message += f"🔹 <b>Duration:</b> {duration:.2f}ms\n"
    
    if user_id:
        message += f"🔹 <b>User:</b> {user_id}\n"
    
    return message


def format_ticket_notification(ticket_data: dict):
    """Форматирует уведомление о тикете"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"🎫 <b>НОВЫЙ ТИКЕТ</b>\n"
    message += f"⏰ {timestamp}\n\n"
    message += f"🆔 <b>ID:</b> {ticket_data.get('id', 'N/A')}\n"
    message += f"📦 <b>Заказ:</b> {ticket_data.get('order_id', 'N/A')}\n"
    message += f"👤 <b>Клиент:</b> {ticket_data.get('client_id', 'N/A')}\n"
    message += f"👨‍💼 <b>Менеджер:</b> {ticket_data.get('manager_id', 'Не назначен')}\n"
    message += f"📝 <b>Описание:</b> {ticket_data.get('description', 'N/A')[:100]}...\n"
    message += f"📊 <b>Статус:</b> {ticket_data.get('status', 'N/A')}\n"
    
    return message


def format_order_notification(order_data: dict):
    """Форматирует уведомление о заказе"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"📦 <b>НОВЫЙ ЗАКАЗ</b>\n"
    message += f"⏰ {timestamp}\n\n"
    message += f"🆔 <b>ID:</b> {order_data.get('id', 'N/A')}\n"
    message += f"👤 <b>Клиент:</b> {order_data.get('client_id', 'N/A')}\n"
    message += f"📍 <b>Откуда:</b> {order_data.get('from_address', 'N/A')[:50]}...\n"
    message += f"📍 <b>Куда:</b> {order_data.get('to_address', 'N/A')[:50]}...\n"
    message += f"💰 <b>Цена:</b> {order_data.get('price', 0)} ₽\n"
    message += f"📊 <b>Статус:</b> {order_data.get('status', 'N/A')}\n"
    
    return message

