"""
Скрипт для настройки Telegram бота.
Помогает получить токен бота и chat_id, и сохранить их в .env файл.
"""
import os
import sys
from pathlib import Path

try:
    import telebot
except ImportError:
    print("Ошибка: Не установлена библиотека pytelegrambotapi")
    print("Установите её командой: pip install pytelegrambotapi")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'


def print_instructions():
    """Выводит инструкции по созданию бота."""
    print("\n" + "=" * 60)
    print("ИНСТРУКЦИЯ ПО СОЗДАНИЮ TELEGRAM БОТА")
    print("=" * 60)
    print("\n1. Откройте Telegram и найдите бота @BotFather")
    print("2. Отправьте команду: /newbot")
    print("3. Введите имя для вашего бота (например: Мои уведомления)")
    print("4. Введите username для вашего бота (должен заканчиваться на 'bot', например: my_notifications_bot)")
    print("5. BotFather отправит вам токен бота (выглядит как: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print("6. Скопируйте этот токен и вставьте его ниже")
    print("\n" + "=" * 60 + "\n")


def get_bot_token():
    """Получает токен бота от пользователя."""
    print_instructions()
    
    while True:
        token = input("Введите токен вашего бота: ").strip()
        
        if not token:
            print("Токен не может быть пустым. Попробуйте снова.")
            continue
        
        # Проверяем формат токена (примерно: цифры:буквы)
        if ':' not in token:
            print("Токен выглядит неверно. Токен должен содержать ':' (например: 123456789:ABCdef...)")
            continue
        
        # Проверяем токен, пытаясь создать бота
        try:
            bot = telebot.TeleBot(token)
            bot_info = bot.get_me()
            print(f"\n✓ Бот успешно подключён!")
            print(f"  Имя бота: {bot_info.first_name}")
            print(f"  Username: @{bot_info.username}")
            return token
        except Exception as e:
            print(f"\n✗ Ошибка подключения к боту: {e}")
            print("Проверьте правильность токена и попробуйте снова.\n")
            retry = input("Попробовать снова? (д/н): ").strip().lower()
            if retry not in ['д', 'y', 'yes', 'да']:
                return None


def get_chat_id(token):
    """Получает chat_id пользователя."""
    print("\n" + "=" * 60)
    print("ПОЛУЧЕНИЕ CHAT_ID")
    print("=" * 60)
    print("\n1. Откройте Telegram и найдите вашего бота (по username, который вы указали)")
    print("2. Нажмите 'Start' или отправьте команду /start боту")
    print("3. Подождите несколько секунд, затем нажмите Enter в этом окне\n")
    
    input("После того как отправили /start боту, нажмите Enter...")
    
    try:
        bot = telebot.TeleBot(token)
        
        print("\nПолучаю информацию о чатах...")
        updates = bot.get_updates()
        
        if not updates:
            print("\n✗ Сообщений не найдено. Убедитесь, что вы отправили /start боту.")
            return None
        
        # Получаем последнее сообщение
        last_update = updates[-1]
        chat_id = last_update.message.chat.id
        
        print(f"\n✓ Chat ID успешно получен!")
        print(f"  Chat ID: {chat_id}")
        print(f"  Имя: {last_update.message.chat.first_name}")
        if last_update.message.chat.last_name:
            print(f"  Фамилия: {last_update.message.chat.last_name}")
        
        # Отправляем тестовое сообщение
        print("\nОтправляю тестовое сообщение...")
        bot.send_message(chat_id, "✅ Настройка успешна! Этот бот будет отправлять вам уведомления.")
        print("✓ Тестовое сообщение отправлено!")
        
        return str(chat_id)
        
    except Exception as e:
        print(f"\n✗ Ошибка получения chat_id: {e}")
        return None


def save_to_env(token, chat_id):
    """Сохраняет токен и chat_id в .env файл."""
    env_lines = []
    
    # Читаем существующий .env файл, если он есть
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            env_lines = [line.strip() for line in f.readlines()]
    
    # Обновляем или добавляем токен
    token_set = False
    chat_id_set = False
    
    for i, line in enumerate(env_lines):
        if line.startswith('TELEGRAM_TOKEN='):
            env_lines[i] = f'TELEGRAM_TOKEN={token}'
            token_set = True
        elif line.startswith('TELEGRAM_ID='):
            env_lines[i] = f'TELEGRAM_ID={chat_id}'
            chat_id_set = True
    
    # Добавляем, если не найдены
    if not token_set:
        env_lines.append(f'TELEGRAM_TOKEN={token}')
    if not chat_id_set:
        env_lines.append(f'TELEGRAM_ID={chat_id}')
    
    # Записываем в файл
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_lines))
        if env_lines and not env_lines[-1].endswith('\n'):
            f.write('\n')
    
    print(f"\n✓ Данные сохранены в файл: {ENV_FILE}")


def main():
    """Основная функция."""
    print("\n" + "=" * 60)
    print("НАСТРОЙКА TELEGRAM БОТА ДЛЯ FORTNITE NOTIFICATIONS")
    print("=" * 60)
    
    # Получаем токен
    token = get_bot_token()
    if not token:
        print("\n✗ Настройка отменена.")
        return
    
    # Получаем chat_id
    chat_id = get_chat_id(token)
    if not chat_id:
        print("\n✗ Не удалось получить chat_id.")
        retry = input("Повторить попытку? (д/н): ").strip().lower()
        if retry in ['д', 'y', 'yes', 'да']:
            chat_id = get_chat_id(token)
            if not chat_id:
                print("\n✗ Настройка не завершена.")
                return
    
    # Сохраняем в .env
    save_to_env(token, chat_id)
    
    print("\n" + "=" * 60)
    print("✓ НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)
    print("\nТеперь вы можете запустить start.bat и бот будет отправлять вам уведомления.")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Настройка прервана пользователем.")
        sys.exit(0)

