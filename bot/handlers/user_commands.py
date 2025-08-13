from aiogram import Router, F, html
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandObject, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from loguru import logger

from bot.filters.base import ChatTypeFilter
from bot.keyboards.keyboards import main_kb, buy_kb
from bot.state import app_state
from bot.repository.user import User
from bot.handlers.fsm_handler import search_film_handler

rt = Router()

class searchFilm(StatesGroup):
    search = State()


@rt.message(ChatTypeFilter("private"), CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    settings = await app_state.settings_repo.get_all()

    if not user:
        await app_state.user_repo.create(User(telegram_id=message.from_user.id, films=[]))

    if command.args:
        fake_message = message.model_copy(update={'text': command.args})
        return await search_film_handler(fake_message, searchFilm.search)

    await message.answer(text=settings.start_message, reply_markup=main_kb(message.from_user.id))

@rt.message(ChatTypeFilter("private"), CommandStart())
async def command_start_handler(message: Message, command: CommandObject) -> None:
    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    settings = await app_state.settings_repo.get_all()

    if not user:
        await app_state.user_repo.create(User(telegram_id=message.from_user.id, films=[]))

    await message.answer(text=settings.start_message, reply_markup=main_kb(message.from_user.id))

@rt.message(F.text == "⭐️ Мои фильмы")
async def user_films(message: Message) -> None:
    settings = await app_state.settings_repo.get_all()
    if settings.is_working == False:
        return await message.answer("В данный момент не работаем, приходите позже")

    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)

    if not user:
        return
    
    if not user.films:
        return await message.answer(text="У Вас пока нет оплаченных фильмов ☹")
    
    msg = "Все ваши фильмы:\n\n"
    
    for id in user.films:
        film = await app_state.film_repo.find_by_film_id(int(id))
        msg += f"{film.film_id}. {film.film_name}\n"

    msg += "\nДля просмотра купленого фильма воспользуйтесь командой /myfilm id_фильма"
    return await message.answer(msg)
        

@rt.message(F.text == "🔎 Ввести код")
async def code_handler(message: Message, state: FSMContext) -> None:
    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    settings = await app_state.settings_repo.get_all()
    if settings.is_working == False:
        return await message.answer("В данный момент не работаем, приходите позже")

    if not user:
        return
    
    await message.answer(settings.code_message)
    await state.set_state(searchFilm.search)

@rt.message(Command(commands="myfilm"))
async def myfilm(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer("Укажите число!")
    
    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    if not int(command.args) in user.films:
        return await message.answer("У вас нет данного фильма")
    
    film = await app_state.film_repo.find_by_film_id(int(command.args))
    if not film:
        return await message.answer("Данного фильма нет в базе данных")
    
    await message.answer("Подождите... Идёт загрузка вашего файла")
    inputfile = FSInputFile(f"./bot/files/{film.path_to_video}")
    msg = (
        f"🎬 {html.bold(film.video_name)}\n\n"
        f"{html.bold('Название:')} {film.film_name}\n\n"
        f"{html.bold('Скачать:')} {html.link(f'💾 ({film.size} MB)', film.link)}\n\n"
        f"{html.bold('Где найти:')} {film.link_found}"
    )
    await message.reply_video(video=inputfile, caption=msg, parse_mode="HTML", disable_web_page_preview=True, protect_content=True)