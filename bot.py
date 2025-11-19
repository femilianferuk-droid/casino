import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
BOT_TOKEN = "8331254765:AAGIzkKOSIekInIyUP-7rVVp3zLFkxIMtgQ"

# Минимальные значения
MIN_BET = 2
MIN_DEPOSIT = 10
MIN_WITHDRAWAL = 30

# ID администратора
ADMIN_CHAT_ID = 7973988177

# Хранение данных
user_balances = {}
admin_mode = {}
user_broadcast = {}  # Для хранения сообщения для рассылки

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Проверка на администратора
    if user_id == ADMIN_CHAT_ID:
        await show_admin_panel(update, context)
        return
    
    if user_id not in user_balances:
        user_balances[user_id] = 0
    
    keyboard = [
        [InlineKeyboardButton("🎲 Кубик", callback_data="game_dice")],
        [InlineKeyboardButton("🏀 Баскетбол", callback_data="game_basketball")],
        [InlineKeyboardButton("⚽ Футбол", callback_data="game_football")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("📥 Пополнение", callback_data="deposit")],
        [InlineKeyboardButton("📤 Вывод", callback_data="withdraw")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            f"🎰 Добро пожаловать в *Nezeex Casino*! 🎰\n\n"
            f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
            f"*Доступные игры:*\n"
            f"🎲 Кубик - угадай число\n"
            f"🏀 Баскетбол - попади в кольцо\n"
            f"⚽ Футбол - забивай голы\n\n"
            f"*Минимальные суммы:*\n"
            f"• Ставка: *{MIN_BET}₽*\n"
            f"• Пополнение: *{MIN_DEPOSIT}₽*\n"
            f"• Вывод: *{MIN_WITHDRAWAL}₽*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            f"🎰 Добро пожаловать в *Nezeex Casino*! 🎰\n\n"
            f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
            f"*Доступные игры:*\n"
            f"🎲 Кубик - угадай число\n"
            f"🏀 Баскетбол - попади в кольцо\n"
            f"⚽ Футбол - забивай голы\n\n"
            f"*Минимальные суммы:*\n"
            f"• Ставка: *{MIN_BET}₽*\n"
            f"• Пополнение: *{MIN_DEPOSIT}₽*\n"
            f"• Вывод: *{MIN_WITHDRAWAL}₽*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать админ-панель"""
    keyboard = [
        [InlineKeyboardButton("👤 Изменить баланс", callback_data="admin_balance")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="main_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    total_users = len(user_balances)
    total_balance = sum(user_balances.values())
    
    if update.message:
        await update.message.reply_text(
            f"🛠️ *Панель администратора Nezeex Casino*\n\n"
            f"📊 Статистика:\n"
            f"• Всего пользователей: {total_users}\n"
            f"• Общий баланс: {total_balance}₽\n\n"
            f"Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            f"🛠️ *Панель администратора Nezeex Casino*\n\n"
            f"📊 Статистика:\n"
            f"• Всего пользователей: {total_users}\n"
            f"• Общий баланс: {total_balance}₽\n\n"
            f"Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def admin_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик изменения баланса"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    admin_mode[user_id] = "waiting_balance_user"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👤 *Изменение баланса*\n\n"
        "Введите ID пользователя и сумму через пробел:\n"
        "Пример: `123456789 100` - установит баланс 100₽ для пользователя 123456789\n\n"
        "Или введите ID пользователя для просмотра текущего баланса:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик рассылки"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    admin_mode[user_id] = "waiting_broadcast"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📢 *Рассылка сообщений*\n\n"
        "Введите сообщение для рассылки всем пользователям:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    total_users = len(user_balances)
    total_balance = sum(user_balances.values())
    active_users = len([uid for uid, balance in user_balances.items() if balance > 0])
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📊 *Статистика Nezeex Casino*\n\n"
        f"• Всего пользователей: {total_users}\n"
        f"• Активных пользователей: {active_users}\n"
        f"• Общий баланс: {total_balance}₽\n"
        f"• Средний баланс: {total_balance/max(total_users, 1):.2f}₽\n\n"
        f"*Топ пользователей по балансу:*\n" +
        "\n".join([f"👤 {uid}: {balance}₽" for uid, balance in 
                  sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:5]]),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений администратора"""
    user_id = update.message.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        return
    
    if user_id not in admin_mode:
        return
    
    text = update.message.text
    
    if admin_mode[user_id] == "waiting_balance_user":
        # Обработка изменения баланса
        try:
            if ' ' in text:
                user_id_to_change, amount = text.split(' ', 1)
                user_id_to_change = int(user_id_to_change)
                amount = int(amount)
                
                user_balances[user_id_to_change] = amount
                
                await update.message.reply_text(
                    f"✅ Баланс пользователя {user_id_to_change} установлен: {amount}₽"
                )
                
                # Пытаемся уведомить пользователя
                try:
                    await context.bot.send_message(
                        user_id_to_change,
                        f"🎰 *Nezeex Casino*\n\n"
                        f"Ваш баланс был изменен администратором!\n"
                        f"💰 Новый баланс: *{amount}₽*",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                    
            else:
                user_id_to_check = int(text)
                balance = user_balances.get(user_id_to_check, 0)
                await update.message.reply_text(
                    f"💰 Баланс пользователя {user_id_to_check}: {balance}₽"
                )
                
        except ValueError:
            await update.message.reply_text("❌ Неверный формат! Используйте: `ID_пользователя сумма`")
        
        admin_mode.pop(user_id, None)
        await show_admin_panel(update, context)
    
    elif admin_mode[user_id] == "waiting_broadcast":
        # Обработка рассылки
        user_broadcast[user_id] = text
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Отправить", callback_data="confirm_broadcast"),
                InlineKeyboardButton("❌ Отменить", callback_data="admin_panel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📢 *Предпросмотр рассылки:*\n\n{text}\n\n"
            f"Получателей: {len(user_balances)} пользователей\n"
            f"Отправить сообщение?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и отправка рассылки"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    message_text = user_broadcast.get(user_id, "")
    
    if not message_text:
        await query.answer("Сообщение для рассылки не найдено!")
        return
    
    # Отправка рассылки
    sent_count = 0
    failed_count = 0
    
    await query.edit_message_text("🔄 Начинаю рассылку...")
    
    for chat_id in user_balances.keys():
        try:
            await context.bot.send_message(
                chat_id,
                f"📢 *Сообщение от Nezeex Casino:*\n\n{message_text}",
                parse_mode='Markdown'
            )
            sent_count += 1
        except:
            failed_count += 1
    
    keyboard = [[InlineKeyboardButton("🔙 В админ-панель", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ *Рассылка завершена!*\n\n"
        f"• Успешно отправлено: {sent_count}\n"
        f"• Не удалось отправить: {failed_count}\n"
        f"• Всего получателей: {len(user_balances)}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    user_broadcast.pop(user_id, None)
    admin_mode.pop(user_id, None)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверка на администратора
    if user_id == ADMIN_CHAT_ID:
        if query.data == "admin_panel":
            await show_admin_panel(update, context)
            return
        elif query.data == "admin_balance":
            await admin_balance_handler(update, context)
            return
        elif query.data == "admin_stats":
            await admin_stats_handler(update, context)
            return
        elif query.data == "admin_broadcast":
            await admin_broadcast_handler(update, context)
            return
        elif query.data == "confirm_broadcast":
            await confirm_broadcast(update, context)
            return
    
    if user_id not in user_balances:
        user_balances[user_id] = 0
    
    if query.data == "balance":
        await show_balance(query, user_id)
    elif query.data == "deposit":
        await deposit(query)
    elif query.data == "withdraw":
        await withdraw(query)
    elif query.data.startswith("game_"):
        await select_game(query, user_id, query.data.split("_")[1])
    elif query.data.startswith("bet_"):
        await place_bet(query, user_id, query.data.split("_")[1])
    elif query.data == "main_menu":
        await main_menu(query, user_id)

async def show_balance(query, user_id):
    """Показать баланс пользователя"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def deposit(query):
    """Пополнение баланса"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📥 *Пополнение баланса*\n\n"
        "Для пополнения баланса, напишите @nezeexsupp, сразу укажите на какую сумму!\n\n"
        f"Минимальное пополнение: *{MIN_DEPOSIT}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def withdraw(query):
    """Вывод средств"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📤 *Вывод средств*\n\n"
        "Для вывода средств, напишите @nezeexsupp, сразу укажите на какую сумму!\n\n"
        f"Минимальный вывод: *{MIN_WITHDRAWAL}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def select_game(query, user_id, game_type):
    """Выбор игры"""
    if user_balances[user_id] < MIN_BET:
        keyboard = [[InlineKeyboardButton("📥 Пополнить баланс", callback_data="deposit")],
                   [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ Недостаточно средств для игры!\n"
            f"Минимальная ставка: {MIN_BET}₽\n"
            f"Ваш баланс: {user_balances[user_id]}₽",
            reply_markup=reply_markup
        )
        return
    
    if game_type == "dice":
        await start_dice_game(query, user_id)
    elif game_type == "basketball":
        await start_basketball_game(query, user_id)
    elif game_type == "football":
        await start_football_game(query, user_id)

async def start_dice_game(query, user_id):
    """Начало игры в кубик"""
    keyboard = [
        [InlineKeyboardButton("1-3", callback_data="bet_dice_low"),
         InlineKeyboardButton("4-6", callback_data="bet_dice_high")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎲 *Игра в кубик*\n\n"
        "Выберите ставку:\n"
        "• 1-3 (x2)\n"
        "• 4-6 (x2)\n\n"
        f"Ваш баланс: {user_balances[user_id]}₽",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_basketball_game(query, user_id):
    """Начало игры в баскетбол"""
    keyboard = [
        [InlineKeyboardButton("Бросок (x3)", callback_data="bet_basketball")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏀 *Баскетбол*\n\n"
        "Сделайте бросок в кольцо!\n"
        "Шанс выигрыша: 30%\n"
        "Коэффициент: x3\n\n"
        f"Ваш баланс: {user_balances[user_id]}₽",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_football_game(query, user_id):
    """Начало игры в футбол"""
    keyboard = [
        [InlineKeyboardButton("Удар по воротам (x2.5)", callback_data="bet_football")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚽ *Футбол*\n\n"
        "Забейте гол!\n"
        "Шанс выигрыша: 40%\n"
        "Коэффициент: x2.5\n\n"
        f"Ваш баланс: {user_balances[user_id]}₽",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def place_bet(query, user_id, game_type):
    """Размещение ставки"""
    bet_amount = MIN_BET
    
    if user_balances[user_id] < bet_amount:
        await query.answer("Недостаточно средств!")
        return
    
    user_balances[user_id] -= bet_amount
    win = False
    multiplier = 1
    
    if game_type == "dice_low":
        dice_roll = random.randint(1, 6)
        win = dice_roll <= 3
        multiplier = 2
        result_text = f"🎲 Выпало: {dice_roll}"
        
    elif game_type == "dice_high":
        dice_roll = random.randint(1, 6)
        win = dice_roll >= 4
        multiplier = 2
        result_text = f"🎲 Выпало: {dice_roll}"
        
    elif game_type == "basketball":
        win = random.random() <= 0.3  # 30% шанс
        multiplier = 3
        result_text = "🏀 " + ("Мяч в корзине! 🎯" if win else "Промах... ❌")
        
    elif game_type == "football":
        win = random.random() <= 0.4  # 40% шанс
        multiplier = 2.5
        result_text = "⚽ " + ("ГОООЛ! ⚽" if win else "Мимо ворот... ❌")
    
    if win:
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        message = f"✅ *ПОБЕДА!*\n\n{result_text}\n\nВы выиграли: {win_amount}₽\nВаш баланс: {user_balances[user_id]}₽"
    else:
        message = f"❌ *ПРОИГРЫШ*\n\n{result_text}\n\nВы проиграли: {bet_amount}₽\nВаш баланс: {user_balances[user_id]}₽"
    
    keyboard = [
        [InlineKeyboardButton("🎮 Играть снова", callback_data=f"game_{game_type.split('_')[1]}")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🔙 В меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def main_menu(query, user_id):
    """Возврат в главное меню"""
    keyboard = [
        [InlineKeyboardButton("🎲 Кубик", callback_data="game_dice")],
        [InlineKeyboardButton("🏀 Баскетбол", callback_data="game_basketball")],
        [InlineKeyboardButton("⚽ Футбол", callback_data="game_football")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("📥 Пополнение", callback_data="deposit")],
        [InlineKeyboardButton("📤 Вывод", callback_data="withdraw")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎰 *Nezeex Casino* 🎰\n\n"
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
        f"Выберите игру:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", show_admin_panel))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
    
    # Запуск бота
    application.run_polling()
    print("Бот Nezeex Casino запущен!")

if __name__ == "__main__":
    main()
