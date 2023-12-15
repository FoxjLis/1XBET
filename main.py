import asyncio
import logging
from aiogram import Bot, Dispatcher
import config
from handlers.Handlers import router
from Funk.News_func import do_parser_news


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()
    dp.include_router(router)
    await do_parser_news()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
