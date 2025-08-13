from aiogram import Router, html, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandObject, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from loguru import logger

from bot.filters.base import ChatTypeFilter
from bot.keyboards.keyboards import admin_kb, main_kb, buy_kb
from bot.config import ADMINS
from bot.state import app_state
from bot.repository.films import Film
from bot.handlers.admin_commands import NewValue, createFilm
from bot.handlers.user_commands import searchFilm
from bot.utils.func import list_all_files

rt = Router()

# Отмена
@rt.message(Command("cancel"))
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено")

# Создание фильма
# id
@rt.message(createFilm.film_id)
async def film_id_film_handler(message: Message, state: FSMContext) -> None:
    if not int(message.text):
        await message.answer("id - число");
        await state.clear()
        return
    
    list = ""
    files = list_all_files("./bot/files")
    for file in files:
        list += f"{file}\n"

    await state.update_data(id=int(message.text))
    await message.answer(f"Принял значение. Введите название иконки с форматом файла:\n\nДоступные файлы:\n{list}")
    await state.set_state(createFilm.icon)
# icon (1.png/jpg)
@rt.message(createFilm.icon)
async def icon_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название файла - это строка");
        await state.clear()
        return
    
    list = ""
    files = list_all_files("./bot/files")
    for file in files:
        list += f"{file}\n"
    
    await state.update_data(icon=str(message.text))
    await message.answer(f"Принял значение. Введите название файла фильма с расширением:\n\nДоступные файлы:\n{list}")
    await state.set_state(createFilm.path_to_video)

# path_to_video
@rt.message(createFilm.path_to_video)
async def video_name_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название файла с расширением - это строка");
        await state.clear()
        return
    
    await state.update_data(path_to_video=str(message.text))
    await message.answer("Принял значение. Введите название видео (не фильма!):")
    await state.set_state(createFilm.video_name)

# video_name (not film_name!)
@rt.message(createFilm.video_name)
async def video_name_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название видео - это строка");
        await state.clear()
        return
    
    await state.update_data(video_name=str(message.text))
    await message.answer("Принял значение. Введите название фильма (не видео!):")
    await state.set_state(createFilm.film_name)
# film name (not video_name!)
@rt.message(createFilm.film_name)
async def film_name_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название фильма - это строка");
        await state.clear()
        return
    
    await state.update_data(film_name=str(message.text))
    await message.answer("Принял значение. Введите размер фильма (в мегабайтах, только число):")
    await state.set_state(createFilm.size)
# size (only int)
@rt.message(createFilm.size)
async def size_film_handler(message: Message, state: FSMContext) -> None:
    if not int(message.text):
        await message.answer("Вес фильма - это число");
        await state.clear()
        return
    
    await state.update_data(size=int(message.text))
    await message.answer("Принял значение. Введите текст который увидет пользователь при покупке:")
    await state.set_state(createFilm.text)
# text (str)
@rt.message(createFilm.text)
async def text_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Текст - это строка");
        await state.clear()
        return
    
    await state.update_data(text=str(message.text))
    await message.answer("Принял значение. Введите прямую ссылку на скачивание:")
    await state.set_state(createFilm.link)
# link (прямая ссылка) (str)
@rt.message(createFilm.link)
async def link_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Ссылка - это строка");
        await state.clear()
        return
    
    await state.update_data(link=str(message.text))
    await message.answer("Принял значение. Введите ссылку на открытый источник ('-' если отстуствует):")
    await state.set_state(createFilm.link_found)
# link_found (источник - ссылка) (str)
@rt.message(createFilm.link_found)
async def link_found_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Ссылка - это строка");
        await state.clear()
        return
    
    await state.update_data(link_found=str(message.text))
    await message.answer("Принял значение. Введите текст в кнопке оплаты, например - 'Оплатить ⭐️ 50'")
    await state.set_state(createFilm.pay_button)
# pay_button (название кнопки) (str)
@rt.message(createFilm.pay_button)
async def pay_button_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название кнопки - это строка");
        await state.clear()
        return
    
    await state.update_data(pay_button=str(message.text))
    await message.answer("Принял значение. Введите сумму звёзд за этот фильм:")
    await state.set_state(createFilm.cost_pay)
# cost_pay (кол-во звёзд) (int)
@rt.message(createFilm.cost_pay)
async def cost_pay_film_handler(message: Message, state: FSMContext) -> None:
    if not int(message.text):
        await message.answer("Название кнопки - это строка");
        await state.clear()
        return
    
    await state.update_data(cost_pay=int(message.text))
    await message.answer("Принял значение. Проверьте все значения (1 - для продолжения):")
    await state.set_state(createFilm.pre_confirm)
# проверка всех значений и подтверждение
@rt.message(createFilm.pre_confirm)
async def cost_pay_film_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    msg = f"""
ID: {data.get("id")}
Иконка: {data.get("icon")}
Видео: {data.get("path_to_video")}
Название видео: {data.get("video_name")}
Название фильма: {data.get("film_name")}
Размер: {data.get("size")}
Прямая ссылка: {data.get("link")}
Ссылка на источник: {data.get("link_found")}
Текст кнопки оплаты: {data.get("pay_button")}
Стоимость фильма: {data.get("cost_pay")}

Текст: 
{data.get("text")}


Для подтверждения напишите что-то, для выхода - /cancel
    """
    await message.answer(msg)
    await state.set_state(createFilm.confirm)
# создание фильма
@rt.message(createFilm.confirm)
async def confirm_film_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film = Film(
        film_id=data.get("id"),
        path_to_video=data.get("path_to_video"),
        icon=data.get("icon"),
        video_name=data.get("video_name"),
        film_name=data.get("film_name"),
        size=data.get("size"),
        text=data.get("text"),
        link=data.get("link"),
        link_found=data.get("link_found"),
        pay_button=data.get("pay_button"),
        cost_pay_button=data.get("cost_pay")
    )
    f = await app_state.film_repo.create(film=film)

    if f:
        await message.answer("Фильм успешно создан!")
    else: 
        await message.answer("При создании фильма произошла ошибка!")

    await state.clear()


# Общий хендлер для новых значений
@rt.message(NewValue.value)
async def new_value_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    res = await app_state.settings_repo.update(data.get("value"), message.text)

    if res == None:
        await message.answer("Неверное значение", reply_markup=admin_kb()); await state.clear(); return
    
    await message.answer(f"Значение '{message.text}' для '{data.get("value")}' успешно установлено", reply_markup=admin_kb())
    await state.clear()

# Хэндлер поиска
@rt.message(searchFilm.search)
async def search_film_handler(message: Message, state: FSMContext) -> None:
    settings = await app_state.settings_repo.get_all()

    if not int(message.text):
        await message.answer("Введите число!", reply_markup=main_kb())
        return await state.clear()
    
    film = await app_state.film_repo.find_by_film_id(int(message.text))
    if film == None:
        return await message.answer(settings.not_found_code_message)
    
    message_build = f"🎬 {html.bold(film.video_name)}\n\n{film.text}"
    starts_btn = film.pay_button
    photo = FSInputFile(f"./bot/files/{film.icon}")

    await message.answer_photo(caption=message_build, reply_markup=buy_kb(starts_btn, f"buy_film|{int(message.text)}"), photo=photo)
    return await state.clear()