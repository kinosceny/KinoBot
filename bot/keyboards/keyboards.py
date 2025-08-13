from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import ADMINS
from loguru import logger

def main_kb(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text="🔎 Ввести код"), KeyboardButton(text="⭐️ Мои фильмы")]
    ]

    if user_telegram_id in ADMINS:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=False)
    return keyboard

def admin_kb():
    kb_list = [
        [KeyboardButton(text="Приветсвие"), KeyboardButton(text="Кнопки"), KeyboardButton(text="Остановить бота")],
        [KeyboardButton(text="Создать новый фильм"), KeyboardButton(text="Все фильмы"), KeyboardButton(text="Изменить цену фильма")],
        [KeyboardButton(text="Назад")]
    ]

    kb = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return kb

def editble_kb():
    kb_list = [
        [KeyboardButton(text="Текст '🔎 Ввести код'"), KeyboardButton(text="Текст '🔎 Ввести код' неудачно")],
        [KeyboardButton(text="Назад")]
    ]

    kb = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return kb

def buy_kb(button, cb_data: str):
    kb_list = [
        [InlineKeyboardButton(text=button, callback_data=cb_data)]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return kb