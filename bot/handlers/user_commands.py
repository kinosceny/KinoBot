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

    callback_data = f"buy_film|{int(message.text)}"
    photo = FSInputFile(f"./bot/previews/{film.icon}")
    logger.debug(callback_data)

    await message.answer_photo(caption=message_build, reply_markup=buy_kb(starts_btn, f"buy_film|{int(message.text)}"), photo=photo)
    return await state.clear()
    
@rt.callback_query(F.data.startswith("buy_film|"))
async def test_payment(callback_query: CallbackQuery):
    await callback_query.answer()

    logger.debug("123123123")

    _, film_id = callback_query.data.split("|")
    film = await app_state.film_repo.find_by_film_id(film_id=film_id)

    await callback_query.bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=f"Фильм #{film.film_id}",
        description="Покупка доступа к фильму",
        payload=f"film|{film.film_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=film.pay_button, amount=film.cost_pay_button)],
        start_parameter="start_parameter"
    )
    await callback_query.answer("123")

@rt.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)  # Всегда подтверждаем

@rt.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    _, film_id = payload.split("|")

    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    film = await app_state.film_repo.find_by_film_id(film_id=film_id)
    val = user.films.append(film_id)
    await app_state.user_repo.update_by_id(message.from_user.id, "films", val)

    inputfile = FSInputFile(f"./bot/videos/{film.path_to_video}")
    msg = f"🎬 {html.bold(film.video_name)}\n\n{html.bold("Название:")} {film.film_name}\n\n{html.bold("Скачать:")} [💾 ({film.size} MB)]({film.link})\n\n{html.bold("Где найти:")} {film.link_found}\n\n{film.text}" 
    
    await message.reply_video(video=inputfile, caption=msg, parse_mode="MarkdownV2")
