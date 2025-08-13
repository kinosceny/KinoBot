from aiogram import Router, html, F
from aiogram.types import Message, FSInputFile, LabeledPrice, SuccessfulPayment, PreCheckoutQuery, CallbackQuery

from loguru import logger

from bot.state import app_state
from bot.config import ADMINS

rt = Router()

@rt.callback_query(F.data.startswith("buy_film"))
async def test_payment(callback_query: CallbackQuery):
    await callback_query.answer()

    _, film_id = callback_query.data.split("|")
    film = await app_state.film_repo.find_by_film_id(film_id=int(film_id))
    settings = await app_state.settings_repo.get_all()

    await callback_query.bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=f"Фильм #{film.film_id}",
        description="Покупка доступа к фильму",
        payload=f"film|{film.film_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"Оплатить ⭐️ {settings.film_cost}", amount=settings.film_cost)]
    )

@rt.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@rt.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    _, film_id = payload.split("|")

    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    film = await app_state.film_repo.find_by_film_id(film_id=int(film_id))
    settings = await app_state.settings_repo.get_all()
    
    new_films = list(user.films) if user.films else []
    new_films.append(int(film_id))

    await app_state.user_repo.update_by_id(message.from_user.id, "films", new_films)

    for admin in ADMINS:
        text = f"💰 Новая покупка (telegramstars)\n\nПользователь @{message.from_user.username} (ID {message.from_user.id}) купил {film.video_name} за {settings.film_cost} XTR"
        await message.bot.send_message(chat_id=admin, text=text)

    await message.answer("Подождите... Идёт загрузка вашего файла")
    inputfile = FSInputFile(f"./bot/files/{film.path_to_video}")
    msg = (
        f"🎬 {html.bold(film.video_name)}\n\n"
        f"{html.bold('Название:')} {html.link(f"{film.film_name}", film.link_found)}\n\n"
        f"{html.bold('Скачать:')} {html.link(f'💾 ({film.size} MB)', film.link)}\n\n"
        f"{html.bold('Где найти:')} {film.link_found}"
    )
    await message.reply_video(video=inputfile, caption=msg, parse_mode="HTML", disable_web_page_preview=True, protect_content=True)