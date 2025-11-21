"""
Обработчики ошибок для бота
"""
import logging
from telegram import Update
from telegram.error import (
    TelegramError,
    NetworkError,
    Conflict,
    BadRequest,
    TimedOut,
    ChatMigrated,
    RetryAfter,
    Forbidden,
    InvalidToken
)
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ошибки, возникающие при работе бота"""
    
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Проверяем тип ошибки
    if isinstance(context.error, Conflict):
        error_msg = (
            "⚠️ Конфликт: другой экземпляр бота уже запущен.\n"
            "Остановите другие экземпляры бота перед запуском."
        )
        logger.error(error_msg)
        # Не отправляем сообщение пользователю, т.к. это системная ошибка
        
    elif isinstance(context.error, BadRequest):
        error_msg = str(context.error)
        logger.error(f"BadRequest: {error_msg}")
        
        # Если ошибка связана с WebApp URL
        if "web app url" in error_msg.lower() and "https" in error_msg.lower():
            logger.warning(
                "⚠️ WebApp URL должен быть HTTPS. "
                "Используйте ngrok или установите правильный URL в .env"
            )
        
        # Пытаемся отправить сообщение пользователю, если есть update
        if update and isinstance(update, Update):
            try:
                if update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ Произошла ошибка при обработке запроса. Попробуйте позже."
                    )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    elif isinstance(context.error, InvalidToken):
        logger.error("InvalidToken: Токен бота неверный или отозван")
        
    elif isinstance(context.error, Forbidden):
        logger.error("Forbidden: Бот заблокирован пользователем")
        
    elif isinstance(context.error, NetworkError):
        logger.warning(f"NetworkError: Проблемы с сетью - {context.error}")
        # Сетевая ошибка, обычно временная
        
    elif isinstance(context.error, TimedOut):
        logger.warning(f"TimedOut: Таймаут запроса - {context.error}")
        
    elif isinstance(context.error, ChatMigrated):
        new_chat_id = context.error.new_chat_id
        logger.info(f"ChatMigrated: Чат перемещен в {new_chat_id}")
        
    elif isinstance(context.error, RetryAfter):
        logger.warning(f"RetryAfter: Слишком много запросов. Подождите {context.error.retry_after} секунд")
        
    elif isinstance(context.error, TelegramError):
        logger.error(f"TelegramError: {context.error}")
        
        # Пытаемся отправить сообщение пользователю
        if update and isinstance(update, Update):
            try:
                if update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
                    )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    else:
        # Неизвестная ошибка
        logger.error(f"Необработанная ошибка: {context.error}", exc_info=context.error)
        
        if update and isinstance(update, Update):
            try:
                if update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ Произошла непредвиденная ошибка. Администратор уведомлен."
                    )
            except Exception:
                pass


def register_error_handler(application):
    """Регистрирует обработчик ошибок в приложении"""
    application.add_error_handler(error_handler)
    logger.info("✅ Обработчик ошибок зарегистрирован")

