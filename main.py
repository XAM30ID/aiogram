import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types.input_file import FSInputFile    

import json

from shifts import Shifts

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="2134346269:AAHZjpA_PNUnUCJ1pSiBkd76ifpsodEUbro")
# Диспетчер
dp = Dispatcher()

NEW_POST = False
SHIFT_ADDING = False


# Проверка на админа
def is_admin(user_id):
    with open("info.json", "r") as f:
        admins = json.load(f)["admins"]
    return user_id in admins

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global SHIFT_ADDING, NEW_POST
    SHIFT_ADDING, NEW_POST = False, False
    if is_admin(message.from_user.id):
        #  Часть для админа
        kb = [
            [types.KeyboardButton(text="Отправить рассылку 📣")],
            [types.KeyboardButton(text="Настроить бота ⚙️")]
        ]

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, 
                                            one_time_keyboard=True,
                                            keyboard=kb)
        await message.answer("👋 Привет, ты - админ и поэтому ты видишь это.\
                            \nЧто хочешь сделать?", reply_markup=keyboard)

    else:
        #  Часть для обычных пользователей
        kb = [
            [types.KeyboardButton(text="Давайте познакомимся поближе 👋")],
            [types.KeyboardButton(text="Я уже бывалый 😎")]
        ]

        keyboard = types.ReplyKeyboardMarkup(input_field_placeholder="Вы были в лагере 'Ника'?",
                                            resize_keyboard=True, 
                                            one_time_keyboard=True,
                                            keyboard=kb)

        await message.answer("😉 Приветствую!\nВы уже были у нас?", 
                            reply_markup=keyboard)


@dp.message(F.text == "Настроить бота ⚙️")
async def set_the_bot(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(callback_data="set_shifts", text="Настроить смены 📝")],
        [types.InlineKeyboardButton(callback_data="set_texts", text="Настроить ответы бота 💬")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer("Что Вы хотите настроить?", 
                         parse_mode=ParseMode.MARKDOWN_V2, 
                         reply_markup=keyboard)
    

@dp.callback_query(F.data == "set_shifts")
async def shifts_settings(callback: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(callback_data="add_shift", text="Добавить смену ➕")],
        [types.InlineKeyboardButton(callback_data="edit_shifts", text="Изменить смены 📝")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    with open("info.json", "r") as f:
        shifts_list = json.load(f)["shifts"]
    if len(shifts_list) == 0:
        mess_text = "Список смен пуст"
    else:
        mess_text = 'Вот список смен:'
        for shift in shifts_list:
            mess_text += f"{shift["title"]}"
    await callback.message.edit_text(text=mess_text, reply_markup=keyboard)


@dp.callback_query(F.data == "add_shift")
async def shift_adding(callback: types.CallbackQuery):
    global SHIFT_ADDING
    SHIFT_ADDING = True
    await callback.message.edit_text(text="Отправьте через разделитель <code>&</code> \
            Название, место, ссылку на форму, описание, даты (в формате дд.мм.гг-дд.мм.гг), \
            заметки при необходимости (их видите только Вы)\nИли отправьте 'Отмена'", 
            parse_mode="html", reply_markup=None)


# Обработчик на новых клиентов
@dp.message(F.text == "Давайте познакомимся поближе 👋")
async def for_news(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(callback_data="more_about", text="Хочу узнать про смены 🌄")],
        [types.InlineKeyboardButton(callback_data="profile", text="Хочу узнать про профиль лагеря 🤔")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer("_*КАКОЙ–ТО ДОКУМЕНТ*_", 
                         parse_mode=ParseMode.MARKDOWN_V2, 
                         reply_markup=keyboard)


# Обработчик на отправку рассылки
@dp.message(F.text == "Отправить рассылку 📣")
async def for_news(message: types.Message):
    global NEW_POST
    if is_admin(message.from_user.id):
        kb = [
            [types.InlineKeyboardButton(callback_data="cancel_posting", text="Отмена ↩️")]
        ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        
        await message.answer("Отправь текст или фотку с текстом для рассылки", 
                            parse_mode=ParseMode.MARKDOWN_V2, 
                            reply_markup=keyboard)
        NEW_POST = True
        


# Обработчик про профиль лагеря
@dp.callback_query(F.data == "profile")
async def about_profile(callback: types.CallbackQuery):
    kb = [
            [types.InlineKeyboardButton(callback_data="more_about", text="Хочу узнать про смены 🌄")],
        ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    f = FSInputFile("static\\images\\gojo.jpg")
    await callback.message.answer_photo(photo=f, caption="_*КАКАЯ–ТО ИНФА*_",
                               parse_mode=ParseMode.MARKDOWN_V2, 
                               reply_markup=keyboard)
    await callback.message.delete()
    

# Обработчик на стареньких и о сменах
@dp.message(F.text == "Я уже бывалый 😎")
async def for_olds(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(callback_data="cost", text="Какие цены на смены? 🪙")],
        [types.InlineKeyboardButton(callback_data="where", text="Где находится лагерь? 🧭")],
        [types.InlineKeyboardButton(callback_data="other", text="Другое")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("_*СПИСОК СМЕН С КРАТКИМ ОПИСАНИЕМ*_", 
                            parse_mode=ParseMode.MARKDOWN_V2, 
                            reply_markup=keyboard)
    await message.delete()

@dp.callback_query(F.data == "more_about")
async def for_olds_cal(callback: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(callback_data="cost", text="Какие цены на смены? 🪙")],
        [types.InlineKeyboardButton(callback_data="where", text="Где находится лагерь? 🧭")],
        [types.InlineKeyboardButton(callback_data="first_time_child", text="Другое")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.answer("_*СПИСОК СМЕН С КРАТКИМ ОПИСАНИЕМ*_", 
                            parse_mode=ParseMode.MARKDOWN_V2, 
                            reply_markup=keyboard)  
    await callback.message.delete()  


# Обработчик на местолполжение лагеря
@dp.callback_query(F.data == "where")
async def where_camp(callback: types.CallbackQuery):
    kb = [
        [types.KeyboardButton(text="Какие цены на смены? 🪙")],
        [types.KeyboardButton(text="Другое")]
    ]

    keyboard = types.ReplyKeyboardMarkup(input_field_placeholder="Какой вопрос Вас интересует?",
                                         resize_keyboard=True, 
                                         one_time_keyboard=True,
                                         keyboard=kb)
    
    await callback.message.answer_location(latitude=55.850127, longitude=52.405631)
    await callback.message.answer("*`ОЦ 'САУЛЫК'`*", 
                         parse_mode=ParseMode.MARKDOWN_V2, 
                         reply_markup=keyboard)


# Обработчик на другое
@dp.message(F.text == "Другое")
async def for_olds(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(callback_data="first_time_child", text="Сможет ли ребенок адаптироваться? 👥")],
        [types.InlineKeyboardButton(callback_data="what_take", text="Что нужно взять на смену? 📃")],
        [types.InlineKeyboardButton(callback_data="how_get_news", text="Как знать, что происходит на смене? 📣")],
        [types.InlineKeyboardButton(callback_data="back", text="Вернуться ↩️")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer("С каким именно вопросом Вам помочь?", 
                         parse_mode=ParseMode.MARKDOWN_V2, 
                         reply_markup=keyboard)

# Здесь про Кирочку (спасибо тебе, если ты это видишь)
@dp.message(F.text == "Почему ты так пристально смотришь на свои часы?")
async def Kira_the_best(message: types.Message):
    text = """
Часы?
Я просто хотел узнать время
Просто, я \- _*Кира*_"""
    await message.answer(text=text,
                         parse_mode=ParseMode.MARKDOWN_V2)


# @dp.message(content_types=types.ContentTypes.PHOTO)
# async def post(message: types.Message):
#     file_id = message.photo[0]['file_id']
#     if is_admin(message.from_user.id) and NEW_POST:
#         with open("info.json", "r") as f:
#             users = json.load(f)["users"]
#         for user in users:
#             if not is_admin(user):
#                 try:
#                     await bot.send_photo(chat_id=user, photo=file_id,
#                                         caption=message.caption)
#                 except Exception as e:
#                     pass
#     await message.answer("Простите, я ещё не так хорошо понимаю Ваш язык 😖",
#                          parse_mode=ParseMode.MARKDOWN_V2)

# Обработчик остальных сообщений
@dp.message()
async def else_messages(message: types.Message):
    global NEW_POST, SHIFT_ADDING 
    if is_admin(message.from_user.id) and NEW_POST:
        with open("info.json", "r") as f:
            users = json.load(f)["users"]
        for user in users:
            if not is_admin(user):
                try:
                    await bot.send_message(chat_id=user, text=message.text)
                except Exception as e:
                    pass
    await message.answer("Простите, я ещё не так хорошо понимаю Ваш язык 😖",
                         parse_mode=ParseMode.MARKDOWN_V2)


@dp.callback_query(F.data == "first_time_child")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("_*ОПИСАНИЕ, ЧТО ВСЁ БУДЕТ ХОРОШО*_", parse_mode=ParseMode.MARKDOWN_V2)

@dp.callback_query(F.data == "what_take")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.edit_text("_*ОПИСАНИЕ, ЧТО С СОБОЙ БРАТЬ*_", parse_mode=ParseMode.MARKDOWN_V2)

@dp.callback_query(F.data == "how_get_news")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.edit_text("_*У НАС БУДЕТ ГРУППА*_", parse_mode=ParseMode.MARKDOWN_V2)

@dp.callback_query(F.data == "back")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("asdasd")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())