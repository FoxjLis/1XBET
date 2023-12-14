from aiogram import Bot
import asyncio
from Main import config
from handlers import kb
from Funk.parsers import parser_football, parser_hockey, parser_volleyball

bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML')
news_set_volley = []
news_set_foot = []
news_set_hockey = []


async def send_last_news(sport):
    if sport == 'football':
        return news_set_foot
    elif sport == 'hockey':
        return news_set_hockey
    elif sport == 'volleyball':
        return news_set_volley


async def do_parser_news(*args) -> None:
    def listing_data():
        post_text_h = parser_hockey()
        if post_text_h != "" and post_text_h not in news_set_hockey:
            news_set_hockey.append(post_text_h)
        post_text_v = parser_volleyball()
        if post_text_v != "" and post_text_v not in news_set_volley:
            news_set_volley.append(post_text_v)
        post_text_f = parser_football()
        if post_text_f != "" and post_text_f not in news_set_foot:
            news_set_foot.append(post_text_f)

    async def news_texting_hockey() -> str:
        news_text_h = ""
        for el in list(news_set_hockey):
            news_text_h += str(el) + "\n"
        return news_text_h

    async def news_texting_volleyball() -> str:
        news_text_v = ""
        for el in list(news_set_volley):
            news_text_v += str(el) + "\n"
        return news_text_v

    async def news_texting_football() -> str:
        news_text_f = ""
        for el in list(news_set_foot):
            news_text_f += str(el) + "\n"
        return news_text_f

    async def edit_message() -> None:
        callback = args[0]
        users_news = args[1]
        user_id = callback.from_user.id
        news_text_h = await news_texting_hockey()
        news_text_v = await news_texting_volleyball()
        news_text_f = await news_texting_football()
        if callback.data == 'footbal' and len(news_set_foot) > 1 and users_news[user_id][0]:
            await bot.send_message(user_id, 'Актуальные новости по футболу:\n' + news_text_f, reply_markup=kb.go_menu)
            news_set_foot.clear()

        if callback.data == "volleyball" and len(news_set_volley) > 1 and users_news[user_id][2]:
            await bot.send_message(user_id, 'Актуальные новости по волейболу:\n' + news_text_v, reply_markup=kb.go_menu)
            news_set_volley.clear()
        if callback.data == "hockey" and len(news_set_hockey) > 1 and users_news[user_id][1]:
            await bot.send_message(user_id, 'Актуальные новости по хоккею:\n' + news_text_h, reply_markup=kb.go_menu)
            news_set_hockey.clear()

    async def send_periodically():
        while True:
            listing_data()
            await asyncio.sleep(120)
            if len(args) == 2:
                await edit_message()

    asyncio.create_task(send_periodically())
