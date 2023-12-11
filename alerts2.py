import kb, config, asyncio
from parsers import parser_football, parser_hockey, parser_volleyball
from aiogram import Bot

bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML')
news_set_volley = set()
news_set_foot = set()
news_set_hockey = set()


async def send_alert_news(callback, users_news):
    print(callback.data)
    id = callback.from_user.id

    def listing_data():

        post_text_h = parser_hockey()
        if post_text_h!="": news_set_hockey.add(post_text_h)
        post_text_v = parser_volleyball()
        if post_text_v!="":news_set_volley.add(post_text_v)
        post_text_f = parser_football()
        if post_text_f!="":news_set_foot.add(post_text_f)

    async def news_texting_hockey():
        news_text_h = ""
        for el in list(news_set_hockey):
            news_text_h += str(el) + "\n"
        return news_text_h

    async def news_texting_volleyball():
        news_text_v = ""
        for el in list(news_set_volley):
            news_text_v += str(el) + "\n"
        return news_text_v

    async def news_texting_football():
        news_text_f = ""
        for el in list(news_set_foot):
            news_text_f += str(el) + "\n"
        return news_text_f

    async def edit_message():
        news_text_h = await news_texting_hockey()
        news_text_v = await news_texting_volleyball()
        news_text_f = await news_texting_football()
        if callback.data == 'footbal' and len(news_set_foot) > 1 and users_news[id][0]:
            await bot.send_message(id, 'Актуальные новости по футболу:\n' + news_text_f, reply_markup=kb.go_menu)
            print(news_set_foot)
            news_set_foot.clear()

        if callback.data == "volleyball" and len(news_set_volley) > 1 and users_news[id][2]:
            await bot.send_message(id, 'Актуальные новости по волейболу:\n' + news_text_v, reply_markup=kb.go_menu)
            print(news_set_volley)
            news_set_volley.clear()
        if callback.data == "hockey" and len(news_set_hockey) > 1 and users_news[id][1]:
            await bot.send_message(id, 'Актуальные новости по хоккею:\n' + news_text_h, reply_markup=kb.go_menu)
            print(news_set_foot)
            news_set_hockey.clear()

    async def send_periodically():
        while True:
            listing_data()
            await asyncio.sleep(300)
            await edit_message()

    asyncio.create_task(send_periodically())
