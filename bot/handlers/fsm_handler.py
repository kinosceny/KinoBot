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
from bot.handlers.admin_commands import NewValue, createFilm, filmValue

rt = Router()

class searchFilm(StatesGroup):
    search = State()

# Отмена
@rt.message(Command("cancel"))
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено")

# Создание фильма

@rt.message(createFilm.film_id)
async def film_id_film_handler(message: Message, state: FSMContext) -> None:
    if not int(message.text):
        await message.answer("id - число");
        await state.clear()
        return

    await state.update_data(id=int(message.text))
    await message.answer(f"Введите название видео:")
    await state.set_state(createFilm.video_name)

@rt.message(createFilm.video_name)
async def video_name_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название видео - это строка");
        await state.clear()
        return
    
    await state.update_data(video_name=str(message.text))
    await message.answer("Введите название фильма:")
    await state.set_state(createFilm.film_name)

@rt.message(createFilm.film_name)
async def film_name_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название фильма - это строка");
        await state.clear()
        return
    
    await state.update_data(film_name=str(message.text))
    await message.answer("Ссылка на imdb/КиноПоиск:")
    await state.set_state(createFilm.link_found)

@rt.message(createFilm.link_found)
async def link_found_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Ссылка - это строка");
        await state.clear()
        return
    
    await state.update_data(link_found=str(message.text))
    await message.answer("Название торрента/онлайн кинотеатра:")
    await state.set_state(createFilm.link_text)

@rt.message(createFilm.link_text)
async def link_found_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Текст ссылки - это строка");
        await state.clear()
        return
    
    await state.update_data(link_text=str(message.text))
    await message.answer("Ссылка торрента/онлайн кинотеатра:")
    await state.set_state(createFilm.link)

@rt.message(createFilm.link)
async def link_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Ссылка - это строка");
        await state.clear()
        return
    
    await state.update_data(link=str(message.text))
    await message.answer("Обложка (название файла с указанием расширения):")
    await state.set_state(createFilm.icon)

@rt.message(createFilm.icon)
async def icon_film_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Ссылка - это строка");
        await state.clear()
        return
    
    await state.update_data(icon=str(message.text))
    await message.answer(f"Видео (название файла с указанием расширения):")
    await state.set_state(createFilm.path_to_video)

@rt.message(createFilm.path_to_video)
async def video_name_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await message.answer("Название файла с расширением - это строка");
        await state.clear()
        return
    
    await state.update_data(path_to_video=str(message.text))
    await message.answer("Введите текст который видит пользователь при покупке:")
    await state.set_state(createFilm.pre_confirm)

@rt.message(createFilm.pre_confirm)
async def preconfirm_film_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(text=str(message.text))
    data = await state.get_data()
    msg = f"""
Код – числовой: {data.get("id")}
Название видео: {data.get("video_name")}
Название фильма: {data.get("film_name")}
Ссылка на imdb/КиноПоиск: {data.get("link_found")}
Название торрента/онлайн кинотеатра: {data.get("link_text")}
Ссылка торрента/онлайн кинотеатра: {data.get("link")}
Обложка: {data.get("icon")}
Видео: {data.get("path_to_video")}

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
        text=data.get("text"),
        link=data.get("link"),
        link_found=data.get("link_found"),
        link_text=data.get("link_text")
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
    if data.get("value") == "film_cost":
        res = await app_state.settings_repo.update(data.get("value"), int(message.text))
    else:
        res = await app_state.settings_repo.update(data.get("value"), message.text)

    if res == None:
        await message.answer("Неверное значение", reply_markup=admin_kb()); await state.clear(); return
    
    await message.answer(f"Значение '{message.text}' для '{data.get("value")}' успешно установлено", reply_markup=admin_kb())
    await state.clear()

@rt.message(filmValue.film_id)
async def filmid_handler(message: Message, state: FSMContext) -> None:
    if not int(message.text):
        await state.set_state(filmValue.film_id)
        return await message.answer("Введите число:");
    
    data = await state.get_data()
    film = await app_state.film_repo.find_by_film_id(int(message.text))
    if film == None:
        await message.answer("Данного фильма нет в базе данных, введите другой id: ")
        await state.set_state(filmValue.film_id);return

    await state.update_data(film_id=int(message.text))
    await message.answer(f"Введите значение для '{data.get("key")}':")
    await state.set_state(filmValue.value)

@rt.message(filmValue.value)
async def filmvalue_handler(message: Message, state: FSMContext) -> None:
    if not str(message.text):
        await state.set_state(filmValue.value)
        return await message.answer("Введите текст:")
    
    await state.update_data(value=message.text)
    data = await state.get_data()

    result = await app_state.film_repo.update_by_film_id(data.get("film_id"), data.get("key"), data.get("value"))
    if result:
        await message.answer("Успешно обновил значение!")
    elif not result:
        await message.answer("Проверьте все значения")

    await state.clear()
    
# Хэндлер поиска
@rt.message(searchFilm.search)
async def search_film_handler(message: Message, state: FSMContext) -> None:
    settings = await app_state.settings_repo.get_all()
    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)

    if not int(message.text):
        await message.answer("Введите число!", reply_markup=main_kb())
        return await state.clear()
    
    film = await app_state.film_repo.find_by_film_id(int(message.text))
    if film == None:
        return await message.answer(settings.not_found_code_message)
    
    if film.film_id in user.films:
        await message.answer("Подождите... Идёт загрузка вашего видео")
        inputfile = FSInputFile(f"./bot/files/{film.path_to_video}")
        msg = (
            f"🎬 {html.bold(film.video_name)}\n\n"
            f"{html.bold('Название:')} {html.link(f"{film.film_name}", film.link_found)}\n\n"
            f"{html.bold('Где найти:')} {html.link(film.link_text, film.link)}"
        )
        return await message.reply_video(
            video=inputfile, 
            caption=msg, 
            parse_mode="HTML", 
            disable_web_page_preview=True, 
            protect_content=True,
            supports_streaming=True,
        )
    
    message_build = f"🎬 {html.bold(film.video_name)}\n\n{film.text}"
    photo = FSInputFile(f"./bot/files/{film.icon}")

    return await message.answer_photo(caption=message_build, reply_markup=buy_kb(f"Оплатить ⭐️ {settings.film_cost}", f"buy_film|{int(message.text)}"), photo=photo)