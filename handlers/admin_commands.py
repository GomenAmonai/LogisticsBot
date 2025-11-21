import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import Database
from models.user import UserRole
from utils.role_helper import check_user_role

logger = logging.getLogger(__name__)
db = Database()


async def set_role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для назначения роли пользователю (только для админов)"""
    user_dict, role = check_user_role(update, db)
    
    if role != UserRole.ADMIN:
        await update.message.reply_text("❌ У вас нет доступа к этой команде. Только администраторы могут использовать эту команду.")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /set_role <user_id> <role>\n\n"
            "Роли: client, manager, admin\n\n"
            "Пример: /set_role 123456789 manager"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        new_role = context.args[1].lower()
        
        if new_role not in [UserRole.CLIENT, UserRole.MANAGER, UserRole.ADMIN]:
            await update.message.reply_text("❌ Неверная роль. Доступные роли: client, manager, admin")
            return
        
        # Проверяем, существует ли пользователь
        target_user = db.get_user(target_user_id)
        if not target_user:
            # Создаем пользователя, если его нет
            db.add_user(
                user_id=target_user_id,
                role=new_role
            )
            await update.message.reply_text(f"✅ Пользователь {target_user_id} создан с ролью {new_role}")
        else:
            # Обновляем роль
            success = db.set_user_role(target_user_id, new_role)
            if success:
                await update.message.reply_text(
                    f"✅ Роль пользователя {target_user_id} изменена на {new_role}"
                )
            else:
                await update.message.reply_text("❌ Ошибка при обновлении роли")
    
    except ValueError:
        await update.message.reply_text("❌ Неверный формат user_id. Должно быть число.")


async def my_role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для просмотра своей роли"""
    user_dict, role = check_user_role(update, db)
    
    role_names = {
        UserRole.CLIENT: "👤 Клиент",
        UserRole.MANAGER: "👨‍💼 Менеджер",
        UserRole.ADMIN: "👑 Администратор"
    }
    
    await update.message.reply_text(
        f"Ваша роль: {role_names.get(role, role)}\n\n"
        f"User ID: {update.effective_user.id}"
    )


def register_admin_commands(application):
    """Регистрирует административные команды"""
    application.add_handler(CommandHandler("set_role", set_role_command))
    application.add_handler(CommandHandler("my_role", my_role_command))

