from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from loguru import logger

from bot.state import app_state
from bot.handlers.fsm_handler import search_film_handler, searchFilm

rt = Router()


@rt.message(F.text,
    lambda message: not message.text.startswith('/'))
async def code_handle(message: Message, state: FSMContext) -> None:
    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    settings = await app_state.settings_repo.get_all()
    if settings.is_working == False:
        return await message.answer("В данный момент не работаем, приходите позже")

    if not user:
        return
    
    return await search_film_handler(message, searchFilm.search)