from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from loguru import logger

from bot.keyboards.keyboards import admin_kb, main_kb, editble_kb
from bot.config import ADMINS
from bot.state import app_state

rt = Router()

class NewValue(StatesGroup):
    value = State()

class createFilm(StatesGroup):
    film_id = State()
    icon = State()
    path_to_video = State()
    video_name = State()
    film_name = State()
    size = State()
    text = State()
    link = State()
    link_found = State()
    pre_confirm = State()
    confirm = State()

# Админ панель
@rt.message(F.text.startswith("⚙️ Админ панель"))
async def admin_panel_handler(message: Message) -> None:
    if message.from_user.id not in ADMINS:
        return
    await message.answer("Панель вызвана", reply_markup=admin_kb())

#Создание нового фильма
@rt.message(F.text.lower() == "создать новый фильм")
async def create_film_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("Вы начали создание нового фильма, введите id для фильма (/cancel - для выхода): ")
    await state.set_state(createFilm.film_id)

#Приветсвтие
@rt.message(F.text.startswith("Приветсвие"))
async def edit_name_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("Введите новое значение для 'start_message' (/cancel - для выхода):")

    await state.set_data({"value": "start_message"})
    await state.set_state(NewValue.value)

#Текст '🔎 Ввести код'
@rt.message(F.text.lower() == "текст '🔎 ввести код'")
async def edit_name_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("Введите новое значение для 'code_message' (/cancel - для выхода):")

    await state.set_data({"value": "code_message"})
    await state.set_state(NewValue.value)

#Текст '🔎 Ввести код' неудачно
@rt.message(F.text.lower() == "текст '🔎 ввести код' неудачно")
async def edit_name_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("Введите новое значение для 'not_found_code_message' (/cancel - для выхода):")

    await state.set_data({"value": "not_found_code_message"})
    await state.set_state(NewValue.value)

@rt.message(F.text.lower() == "кнопки")
async def edit_name_handler(message: Message) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("Открыты ответы кнопок", reply_markup=editble_kb())

#Назад в start меню
@rt.message(F.text.lower() == "назад")
async def create_film_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMINS:
        return
    settings = await app_state.settings_repo.get_all()
    await message.answer(settings.start_message, reply_markup=main_kb(message.from_user.id))

# Все фильмы
@rt.message(F.text.lower() == "все фильмы")
async def all_films(message: Message) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    settings = await app_state.settings_repo.get_all()
    films = await app_state.film_repo.get_all()
    if films == None:
        return await message.answer("Сейчас в базе данных отсутствуют фильмы", reply_markup=admin_kb())
    
    msg = "Список доступных фильмов:\n\n"
    for film in films:
        msg += f"{film.film_id}. {film.film_name} ({settings.film_cost} ⭐️)\n"

    msg += "\nДля удаления используйте команду /delete_film id_фильма"
    return await message.answer(text=str(msg), reply_markup=admin_kb())

@rt.message(F.text.lower() == "остановить бота")
async def stop_bot(message: Message) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    settings = await app_state.settings_repo.get_all()
    if settings.is_working == True:
        await app_state.settings_repo.update("is_working", False)
        return await message.answer("Теперь бот не отвечает на кнопки для пользователей")
    elif settings.is_working == False:
        await app_state.settings_repo.update("is_working", True)
        return await message.answer("Теперь бот отвечает на кнопки для пользователей")
    
@rt.message(F.text.lower() == "изменить цену фильма")
async def stop_bot(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("Введите новое значение для 'film_cost' (/cancel - для выхода):")

    await state.set_data({"value": "film_cost"})
    await state.set_state(NewValue.value)

@rt.message(Command(commands="delete_film"))
async def delete_film(message: Message, command: CommandObject) -> None:
    if message.from_user.id not in ADMINS:
        return
    
    if not command.args:
        return await message.answer("Укажите число!")
    
    films = await app_state.film_repo.find_by_film_id(int(command.args))
    if films == None:
        return await message.answer("Данный фильм отстутствует в базе данных")
    
    await app_state.film_repo.delete_by_film_id(int(command.args))
    return await message.answer("Фильм успешно удален", reply_markup=admin_kb())