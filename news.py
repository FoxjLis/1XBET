import kb, config, asyncio
from parsers import parser_football, parser_hockey, parser_volleyball
from aiogram import Bot

news_set_volley = set()
news_set_foot = set()
news_set_hockey = set()


async def new_news():
    def listing_data():
        post_text_h = parser_hockey()
        news_set_hockey.add(post_text_h)
        post_text_v = parser_volleyball()
        news_set_volley.add(post_text_v)
        post_text_f = parser_football()
        news_set_foot.add(post_text_f)

    async def edit_message():
        return news_set_volley

    async def send_periodically():
        while True:
            listing_data()
            await asyncio.sleep(20)
            print(news_set_foot)
            print(news_set_hockey)
            await edit_message()

    asyncio.create_task(send_periodically())
