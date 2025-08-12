from aiogram import Router, F, html
from aiogram.types import Message, FSInputFile, LabeledPrice, SuccessfulPayment, PreCheckoutQuery, CallbackQuery
from aiogram.filters import CommandObject, CommandStart

from loguru import logger

from bot.filters.base import ChatTypeFilter
from bot.keyboards.keyboards import main_kb, buy_kb
from bot.state import app_state
from bot.repository.user import User
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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
        film_number = int(command.args)
        logger.debug(film_number)

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
    
    ...

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