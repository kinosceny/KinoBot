import asyncio
import bot.migrations_runner as migrations_runner

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers import user_commands, admin_commands, fsm_handler, invoice_handler
from bot.config import BOT_TOKEN
from bot.state import app_state

from loguru import logger

dp = Dispatcher()

async def startup() -> None:
    migrations_runner.apply()
    await app_state.startup()

async def shutdown() -> None:
    await app_state.shutdown()

async def main() -> None:
    await startup()
    logger.info("Запуск бота..."); bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)); logger.debug("Бот успешно запущен")

    logger.info("Загрузка роутеров..."); 
    dp.include_routers(
        user_commands.rt,
        admin_commands.rt,
        #invoice_handler.rt,
        fsm_handler.rt,
    )
    logger.debug("Роутер [user_commands] загружен")
    logger.debug("Роутер [admin_commands] загружен")
    logger.debug("Роутер [fsm_handler] загружен")
    logger.debug("Роутер [invoice_handler] загружен")

    await dp.start_polling(bot,
                           allowed_updates=["message", "inline_query", "chat_member", "my_chat_member"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
        logger.info("Exiting...")