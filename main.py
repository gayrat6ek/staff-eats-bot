#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few call⬅️ Назад functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from orders.orders import get_user,get_department,create_order,create_client,logout_reqeust,client_update
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence
)


from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN_HELPDESK = os.environ.get('BOT_TOKEN')
LOGIN, MANU, CONFIRMATION, MEALS, BREADS, SALADS, LOGOUT= range(7)
manu_keyboard = [['Подать заявку 🥘','Настройки ⚙️']]
BREAD_CATEGORY =3
MEAL_CATEGORY = 1
SALAD_CATEGORY = 2


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    current_client = get_user(update.message.from_user.id)
    if current_client["items"] and current_client['items'][0]['department_id']:
        context.user_data['department_id'] = current_client['items'][0]['department_id']
        context.user_data['client_id'] = current_client['items'][0]['id']
        welcome_text = f"Вы успешно вошли в программу, ваш филиал -- " +current_client['items'][0]['department']['name']
        await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return  MANU
    await update.message.reply_text("Добро пожаловать в бот StaffEats🥘 Здесь можете оформлять заявки на стафф-питание. \n"
                                    "Для дальнейшей работы пожалуйста введите пароль который предоставил Системный администратор.")
    return LOGIN


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected"""
    department = get_department(update.message.text)
    if department['items']:
        context.user_data['department_id'] = department['items'][0]['id']
        current_branch = department['items'][0]['name']
        current_client = get_user(update.message.from_user.id)
        if current_client["items"]:
            context.user_data['client_id'] = current_client['items'][0]['id']
            data_update = {
                "id": current_client['items'][0]['id'],
                "department_id": context.user_data['department_id'],
            }
            client_update(data_update)
        else:

            data = {
                "telegram_id": str(update.message.from_user.id),
                "department_id": context.user_data['department_id'],
                "name": update.message.from_user.first_name,
                "username": update.message.from_user.username
            }
            cleint_creation = create_client(data)
            context.user_data['client_id'] = cleint_creation['id']
        await update.message.reply_text( f"Вы успешно вошли в программу, ваш филиал -- {current_branch}", reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return MANU
    await update.message.reply_text('Неверный пароль, попробуйте еще раз')
    return LOGIN


async  def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if update.message.text == 'Выйти с профиля':
        data = {
            "telegram_id": str(update.message.from_user.id),
        }
        logout = logout_reqeust(data)
        await update.message.reply_text('Вы успешно вышли из профиля', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    await update.message.reply_text('Главная страница', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
    return MANU

async def manu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if update.message.text == 'Подать заявку 🥘':
        await update.message.reply_text('🍛Напишите количество порции еды (число):', reply_markup=ReplyKeyboardMarkup([['⬅️ Назад']],resize_keyboard=True))
        return MEALS
    elif update.message.text == 'Настройки ⚙️':
        await update.message.reply_text("Settings", reply_markup=ReplyKeyboardMarkup([['Выйти с профиля','⬅️ Назад']],resize_keyboard=True))
        return LOGOUT
    else:
        await update.message.reply_text('Главная страница', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return MANU




async def meals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == '⬅️ Назад':
        await update.message.reply_text('Главная страница', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return MANU

    try:
        int(update.message.text)
    except:
        await update.message.reply_text('🍛Напишите количество порции еды (число):')
        return MEALS


    context.user_data['meals'] = update.message.text
    await update.message.reply_text('🥖Напишите количество порции хлеба (число):', reply_markup=ReplyKeyboardMarkup([['⬅️ Назад']],resize_keyboard=True))
    return BREADS

async def breads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == '⬅️ Назад':
        await update.message.reply_text('🍛Напишите количество порции еды (число):', reply_markup=ReplyKeyboardMarkup([['⬅️ Назад']],resize_keyboard=True))
        return MEALS
    try:
        int(update.message.text)
    except:
        await update.message.reply_text('🥖Напишите количество порции хлеба (число)')
        return BREADS


    context.user_data['breads'] = update.message.text
    await update.message.reply_text('🥗Напишите количество порции салата (число):', reply_markup=ReplyKeyboardMarkup([['⬅️ Назад']],resize_keyboard=True))
    return SALADS


async def salads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == '⬅️ Назад':
        await update.message.reply_text('🥖Напишите количество порции хлеба (число):', reply_markup=ReplyKeyboardMarkup([['⬅️ Назад']],resize_keyboard=True))
        return BREADS

    try:
        int(update.message.text)
    except:
        await update.message.reply_text('🥗Напишите количество порции салата (число):')
        return SALADS

    context.user_data['salads'] = update.message.text

    confirmation_text = f"Порции еды: {context.user_data['meals']}\nПорции хлеба: {context.user_data['breads']}\nПорции салата: {context.user_data['salads']}"
    await update.message.reply_text(confirmation_text, reply_markup=ReplyKeyboardMarkup([['Подтвердить✅', 'Отменить❌']],resize_keyboard=True))
    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Отменить❌':
        await update.message.reply_text('Buyurtma bekor qilindi', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return MANU

    if update.message.text == 'Подтвердить✅':
        data = {
            "orderitems":[
                {
                    "group_id": MEAL_CATEGORY,
                    "amount": context.user_data['meals']
                },
                {
                    "group_id": BREAD_CATEGORY,
                    "amount": context.user_data['breads']
                },
                {
                    "group_id": SALAD_CATEGORY,
                    "amount": context.user_data['salads']
                }
            ],
            "department_id": context.user_data['department_id'],
            "client_id": context.user_data['client_id']
        }
        order = create_order(data)
        await update.message.reply_text('Ваша заявка принята☑️', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True ))
        return MANU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text("Ko'rishguncha", reply_markup=ReplyKeyboardRemove()
                                    )

    return ConversationHandler.END




def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="botcommunication")

    application = Application.builder().token(BOT_TOKEN_HELPDESK).persistence(persistence).build()
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOGIN: [MessageHandler(filters.ALL, login)],
            MANU: [MessageHandler(filters.ALL, manu)],
            MEALS: [MessageHandler(filters.ALL, meals)],
            BREADS: [MessageHandler(filters.ALL, breads)],
            SALADS: [MessageHandler(filters.ALL, salads)],
            CONFIRMATION: [MessageHandler(filters.ALL, confirmation)],
            LOGOUT: [MessageHandler(filters.ALL, logout)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
