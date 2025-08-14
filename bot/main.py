import asyncio
import bot.migrations_runner as migrations_runner

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode

from bot.handlers import user_commands, admin_commands, fsm_handler, invoice_handler, echo
from bot.config import BOT_TOKEN, API_SERVER
from bot.state import app_state

from loguru import logger

session = AiohttpSession(api=TelegramAPIServer.from_base(API_SERVER)) 

dp = Dispatcher()

async def startup() -> None:
    migrations_runner.apply()
    await app_state.startup()

async def shutdown() -> None:
    await app_state.shutdown()

async def main() -> None:
    await startup()
    logger.info("Запуск бота..."); bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML)); logger.debug("Бот успешно запущен")

    logger.info("Загрузка роутеров..."); 
    dp.include_router(user_commands.rt)
    dp.include_router(admin_commands.rt)
    dp.include_router(invoice_handler.rt)
    dp.include_router(fsm_handler.rt)
    dp.include_router(echo.rt)

    logger.debug("Роутер [user_commands] загружен")
    logger.debug("Роутер [admin_commands] загружен")
    logger.debug("Роутер [fsm_handler] загружен")
    logger.debug("Роутер [invoice_handler] загружен")
    logger.debug("Роутер [echo] загружен")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
        logger.info("Exiting...")