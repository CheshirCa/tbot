from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import paramiko
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# ============================================
# НАСТРОЙКИ БОТА И МИКРОТИКА
# ============================================

# Токен бота Telegram (заменить на реальный)
TOKEN = "0000000000:ZZZZZZZZZZZZZZZZZZZZZZZZZ-XXXXXXXXX" 

# Параметры подключения к MikroTik
MIKROTIK_IP = "192.168.0.1"  # IP-адрес MikroTik
MIKROTIK_USER = "tbot"  # Пользователь для SSH-подключения
MIKROTIK_SSH_PORT = 22  # Порт SSH (можно изменить при необходимости)
SSH_KEY_PATH = "C:/Users/User/.ssh/mikrotik_bot_key"  # Путь к приватному SSH-ключу
REBOOT_PASSWORD = "12345678901"  # Пароль для подтверждения перезагрузки

# Список разрешенных пользователей (ID и username), второе значение - как бот будет обращаться к пользователю
ALLOWED_USERS = {
    # По ID (числа)
    111111111: "Администратор",
    # По username (строки)
    "BotAdmin": "Админ",
}

# Состояния для ConversationHandler (используется для обработки диалога перезагрузки)
PASSWORD_CONFIRMATION = range(1)

# Настройки логгирования
LOG_FILE = "bot.log"  # Имя файла лога
LOG_MAX_SIZE = 5 * 1024 * 1024  # Максимальный размер лог-файла (5 MB)
LOG_BACKUP_COUNT = 3  # Количество бэкап-копий логов

# ============================================
# НАСТРОЙКА ЛОГГИРОВАНИЯ
# ============================================

def setup_logging():
    """Настройка системы логирования с ротацией файлов"""
    os.makedirs("logs", exist_ok=True)  # Создаем папку для логов, если ее нет
    
    # Формат логов: время - имя - уровень - сообщение
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Уровень логирования INFO и выше
    
    # Обработчик для ротации логов (создает новые файлы при достижении максимального размера)
    file_handler = RotatingFileHandler(
        filename=f"logs/{LOG_FILE}",
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# Инициализация логгера
logger = setup_logging()

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

async def log_activity(action: str, user: str, details: str = ""):
    """Логирование действий пользователей"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {action} - Пользователь: {user}"
    if details:
        log_message += f" - Детали: {details}"
    logger.info(log_message)

async def check_access(update: Update) -> bool:
    """Проверка, есть ли у пользователя доступ к боту"""
    user = update.effective_user
    if not user:
        await log_activity("Попытка доступа", "Unknown", "Не удалось определить пользователя")
        return False

    # Проверяем, есть ли пользователь в списке разрешенных (по ID или username)
    if user.id in ALLOWED_USERS or (user.username and user.username in ALLOWED_USERS):
        await log_activity("Доступ разрешен", f"ID:{user.id}" if user else "Unknown")
        return True

    # Если пользователь не найден в списке разрешенных
    await log_activity("Доступ запрещен", f"ID:{user.id if user else 'Unknown'}")
    await update.message.reply_text("🚫 Доступ запрещен!\nОбратитесь к администратору.")
    return False

def ssh_command_sync(command: str) -> str:
    """Синхронное выполнение команды на MikroTik через SSH с использованием ключа"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Автоматически добавляем ключ хоста
    try:
        # Загружаем приватный ключ для аутентификации
        private_key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
        # Устанавливаем соединение с MikroTik
        ssh.connect(
            hostname=MIKROTIK_IP,
            port=MIKROTIK_SSH_PORT,
            username=MIKROTIK_USER,
            pkey=private_key,
            timeout=10
        )
        # Выполняем команду и получаем результат
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()
        return output if output else "Команда выполнена успешно"
    except Exception as e:
        logger.error(f"SSH ошибка: {str(e)}", exc_info=True)
        return f"Ошибка: {str(e)}"
    finally:
        ssh.close()  # Всегда закрываем соединение

async def ssh_command(command: str) -> str:
    """Асинхронная обертка для ssh_command_sync"""
    return await asyncio.get_event_loop().run_in_executor(None, ssh_command_sync, command)

# ============================================
# ОБРАБОТЧИКИ КОМАНД БОТА
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start - главное меню"""
    if not await check_access(update):
        return
        
    user = update.effective_user
    # Создаем клавиатуру с основными командами
    keyboard = [
        ["Показать интерфейсы", "Проверить ping"],
        ["Перезагрузить MikroTik", "Показать ресурсы"]
    ]
    await update.message.reply_text(
        f"Привет, {ALLOWED_USERS.get(user.id, ALLOWED_USERS.get(user.username, 'пользователь'))}!\n"
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)  # Отправляем клавиатуру
    )
    await log_activity("Старт бота", f"ID:{user.id}")

async def reboot_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрос подтверждения перезагрузки (первый шаг диалога)"""
    await update.message.reply_text(
        "⚠️ Для перезагрузки MikroTik введите пароль:"
    )
    return PASSWORD_CONFIRMATION  # Переходим в состояние ожидания пароля

async def check_reboot_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверка пароля для перезагрузки (второй шаг диалога)"""
    user_input = update.message.text
    if user_input == REBOOT_PASSWORD:
        # Если пароль верный - выполняем перезагрузку
        await log_activity("Перезагрузка MikroTik", f"ID:{update.effective_user.id}")
        await ssh_command("/system reboot")
        await update.message.reply_text("🔌 MikroTik перезагружается...")
    else:
        # Если пароль неверный - сообщаем об ошибке
        await log_activity("Неверный пароль перезагрузки", f"ID:{update.effective_user.id}")
        await update.message.reply_text("❌ Неверный пароль! Действие отменено.")
    
    # Возвращаемся в главное меню
    await start(update, context)
    return ConversationHandler.END  # Завершаем диалог

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (основных команд)"""
    if not await check_access(update):
        return
        
    text = update.message.text
    user = update.effective_user
    
    try:
        if text == "Показать интерфейсы":
            await log_activity("Запрос интерфейсов", f"ID:{user.id}")
            result = await ssh_command("/interface print")  # Получаем список интерфейсов
            await update.message.reply_text(f"📶 Интерфейсы:\n{result}")
        elif text == "Проверить ping":
            await log_activity("Проверка ping", f"ID:{user.id}")
            result = await ssh_command("/ping 8.8.8.8 count=4")  # Пингуем Google DNS
            await update.message.reply_text(f"🏓 Ping:\n{result}")
        elif text == "Перезагрузить MikroTik":
            return await reboot_confirmation(update, context)  # Начинаем диалог перезагрузки
        elif text == "Показать ресурсы":
            await log_activity("Запрос ресурсов", f"ID:{user.id}")
            result = await ssh_command("/system resource print")  # Получаем информацию о ресурсах
            await update.message.reply_text(f"📊 Ресурсы:\n{result}")
    except Exception as e:
        error_msg = f"Ошибка при обработке команды: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await update.message.reply_text(f"⚠️ {error_msg}")

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Основная функция запуска бота"""
    try:
        # Создаем приложение бота
        application = Application.builder().token(TOKEN).build()
        
        # Создаем обработчик диалога для перезагрузки
        reboot_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^Перезагрузить MikroTik$"), reboot_confirmation)],
            states={
                PASSWORD_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_reboot_password)],
            },
            fallbacks=[CommandHandler("start", start)],  # Возврат в главное меню
        )
        
        # Регистрируем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(reboot_handler)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("Бот запущен и готов к работе")
        application.run_polling()  # Запускаем бота в режиме polling
    except Exception as e:
        logger.critical(f"Фатальная ошибка при запуске бота: {str(e)}", exc_info=True)
    finally:
        logger.info("Бот остановлен")

if __name__ == "__main__":
    main()

