#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from orders.orders import get_user,get_department,create_order,create_client
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
LOGIN, MANU,CONFIRMATION,MEALS,BREADS,SALADS = range(6)
manu_keyboard = [['Buyurtma berish']]
BREAD_CATEGORY =3
MEAL_CATEGORY = 1
SALAD_CATEGORY = 2


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    current_client = get_user(update.message.from_user.id)
    if current_client["items"] and current_client['items'][0]['department_id']:
        context.user_data['department_id'] = current_client['items'][0]['department_id']
        context.user_data['client_id'] = current_client['items'][0]['id']
        await update.message.reply_text(f"Xush galdinigiz sizning fillialingiz", reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return  MANU
    await update.message.reply_text('Iltimos FIllial parolini kiriting')
    return LOGIN


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected"""
    department = get_department(update.message.text)
    if department['items']:
        context.user_data['department_id'] = department['items'][0]['id']
        current_branch = department['items'][0]['name']
        await update.message.reply_text( f"Xush galdingiz, sizing fillialingiz {current_branch}", reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))

        data = {
            "telegram_id": str(update.message.from_user.id),
            "department_id": context.user_data['department_id'],
            "name": update.message.from_user.first_name,
            "username": update.message.from_user.username

        }

        cleint_creation = create_client(data)
        context.user_data['client_id'] = cleint_creation['id']

        return MANU
    await update.message.reply_text('Bunday parolli fillial topilmadi, iltimos qaytadan kiriting')
    return LOGIN


async def manu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text('NEcha porsiya ovqat zakaz qilmoqchisiz, faqat raqam yuboring. masalan 5', reply_markup=ReplyKeyboardMarkup([['Back']],resize_keyboard=True))
    return MEALS

async def meals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Back':
        await update.message.reply_text('Buyurtma berish', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return MANU

    try:
        int(update.message.text)
    except:
        await update.message.reply_text('ovqat uchun Raqam kiriting, masalan 5')
        return MEALS


    context.user_data['meals'] = update.message.text
    await update.message.reply_text('Qanday non xohlaysiz', reply_markup=ReplyKeyboardMarkup([['Back']],resize_keyboard=True))
    return BREADS

async def breads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Back':
        await update.message.reply_text('NEcha porsiya ovqat zakaz qilmoqchisiz, faqat raqam yuboring. masalan 5', reply_markup=ReplyKeyboardMarkup([['Back']],resize_keyboard=True))
        return MEALS
    try:
        int(update.message.text)
    except:
        await update.message.reply_text('non uchun raqam kiriting Raqam kiriting,')
        return BREADS

    print(context.user_data['meals'])

    context.user_data['breads'] = update.message.text
    await update.message.reply_text('Qanday salat xohlaysiz', reply_markup=ReplyKeyboardMarkup([['Back']],resize_keyboard=True))
    return SALADS


async def salads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Back':
        await update.message.reply_text('Qanday non xohlaysiz', reply_markup=ReplyKeyboardMarkup([['Back']],resize_keyboard=True))
        return BREADS

    try:
        int(update.message.text)
    except:
        await update.message.reply_text('salad uchun raqam kiriting, Raqam kiriting')
        return SALADS

    context.user_data['salads'] = update.message.text

    confirmation_text = f"Ovqatlar: {context.user_data['meals']},  Nonlar: {context.user_data['breads']}, Salatlar: {context.user_data['salads']}"
    await update.message.reply_text(confirmation_text, reply_markup=ReplyKeyboardMarkup([['Tasdiqlash', 'Bekor qilish']],resize_keyboard=True))
    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Bekor qilish':
        await update.message.reply_text('Buyurtma bekor qilindi', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True))
        return MANU

    if update.message.text == 'Tasdiqlash':
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
        await update.message.reply_text('Buyurtma tasdiqlandi', reply_markup=ReplyKeyboardMarkup(manu_keyboard, resize_keyboard=True ))

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
            CONFIRMATION: [MessageHandler(filters.ALL, confirmation
            )],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
