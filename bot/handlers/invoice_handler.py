from aiogram import Router, html, F
from aiogram.types import Message, FSInputFile, LabeledPrice, SuccessfulPayment, PreCheckoutQuery, CallbackQuery

from loguru import logger

from bot.state import app_state


rt = Router()

@rt.callback_query(F.data.startswith("buy_film"))
async def test_payment(callback_query: CallbackQuery):
    await callback_query.answer()

    _, film_id = callback_query.data.split("|")
    film = await app_state.film_repo.find_by_film_id(film_id=int(film_id))

    await callback_query.bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=f"Фильм #{film.film_id}",
        description="Покупка доступа к фильму",
        payload=f"film|{film.film_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=film.pay_button, amount=film.cost_pay_button)]
    )

@rt.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)  # Всегда подтверждаем

@rt.message(F.successfull_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    _, film_id = payload.split("|")

    user = await app_state.user_repo.get_by_telegram_id(message.from_user.id)
    film = await app_state.film_repo.find_by_film_id(film_id=int(film_id))
    val = user.films.append(film_id)
    await app_state.user_repo.update_by_id(message.from_user.id, "films", val)

    inputfile = FSInputFile(f"./bot/videos/{film.path_to_video}")
    msg = f"🎬 {html.bold(film.video_name)}\n\n{html.bold("Название:")} {film.film_name}\n\n{html.bold("Скачать:")} [💾 ({film.size} MB)]({film.link})\n\n{html.bold("Где найти:")} {film.link_found}\n\n{film.text}" 
    
    await message.reply_video(video=inputfile, caption=msg, parse_mode="MarkdownV2")