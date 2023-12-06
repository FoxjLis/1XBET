from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from Requests import (
    match_history_between_teams,
    player_stat,
    team_members,
    team_stat
)
import alerts2
import kb
import parsers
import text
import config

bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML')
news_set_volley = set()
news_set_foot = set()
news_set_hockey = set()

router = Router()
users = dict()
users_input = dict()
users_news = dict()
team_fight_history = dict()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.callback_query(F.data == 'menu')
async def news(callback: CallbackQuery):
    user_id = callback.from_user.id
    users[user_id] = []
    await callback.message.edit_text(text=text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == 'back')
async def news_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    options = ['search_directory', 'news', 'alerts', 'catalog4']
    if users[user_id][-2] in options:
        await select_an_option(callback, users[user_id][-2])
        users[user_id] = [users[user_id][0]]
    elif users[user_id][-3] == 'search_directory':
        users[user_id] = users[user_id][:-1:]
        await distribute(callback)


async def select_an_option(callback: CallbackQuery, category: str):
    user_id = callback.from_user.id
    users[user_id] = [category]
    await callback.message.edit_text(text='🏆 Выберите вид спорта', reply_markup=kb.kinds_sports)


@router.callback_query(F.data.in_(['news', 'alerts', 'search_directory']))
async def news_callback(callback: CallbackQuery):
    await select_an_option(callback, callback.data)


@router.callback_query(F.data.in_(['football', 'hockey', 'volleyball']))
async def sport_news(callback: CallbackQuery):
    await distribute(await add_a_sport(callback))


@router.callback_query(F.data.in_(['player', 'team', 'history']))
async def type_stat(callback: CallbackQuery):
    user_id = callback.from_user.id
    users[user_id].append(callback.data)

    if callback.data == 'player':
        await callback.message.edit_text(
            text='🔎 Введите Фамилию и имя игрока <b>через пробел</b> с <b>заглавной буквы</b>\nПример: "Мишуров Андрей"',
            reply_markup=kb.back)
    elif callback.data == 'team':
        await callback.message.edit_text(text='🔎 Введите Название команды c заглавной буквы. Пример: "Лада"',
                                         reply_markup=kb.back)
    elif callback.data == 'history':
        await callback.message.edit_text(
            text='🔎 Введите название первой команды c <b>заглавной буквы и город</b>, за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
        team_fight_history[user_id] = []
    users_input[user_id] = [0]


async def print_stat(message):
    user_id = message.from_user.id
    if users[user_id][-1] == 'player':
        if player_stat(users_input[user_id][0]) != '':
            msg = await message.answer(text=player_stat(users_input[user_id][0]), reply_markup=kb.back)
        else:
            msg = await message.answer('Игрок с таким именем не найден ❌ Попробуйте ещё раз!', reply_markup=kb.back)
        return msg.message_id
    if users[user_id][-1] == 'team':
        if team_stat(users_input[user_id][0]) != '':
            stat = team_stat(users_input[user_id][0])
            members = team_members(users_input[user_id][0])
            msg = await message.answer(text=f'{members}\n\n{stat}', reply_markup=kb.back)
        else:
            msg = await message.answer('Команда с таким названием не найдена ❌ Попробуйте ещё раз!\nВведите название команды:',
                                       reply_markup=kb.back)
        return msg.message_id
    if users[user_id][-1] == 'history':
        if team_fight_history[user_id] == []:
            team_fight_history[user_id].append(users_input[user_id][0])
            msg = await message.answer(
                f'Первая команда - {team_fight_history[user_id][0]} ✅\nВведите название второй команды, например: "Ак Барс Казань"',
                reply_markup=kb.back)
        else:
            team_fight_history[user_id].append(users_input[user_id][0])
            text = match_history_between_teams(team_fight_history[user_id][0], team_fight_history[user_id][1])
            if text == '' or team_fight_history[user_id][0]==team_fight_history[user_id][1]:
                text1 = 'не найдена ❌ Попробуйте ещё раз! Введите название первой команды'
            else:
                text1 = 'найдена ✅'
            msg = await message.answer(
                text=f'История противостояний команд {team_fight_history[user_id][0]} и {team_fight_history[user_id][1]} {text1}\n\n{text}',
                reply_markup=kb.back)
            team_fight_history[user_id] = []
        print(team_fight_history)
        return msg.message_id


async def add_a_sport(callback):
    sport = callback.data
    user_id = callback.from_user.id
    users[user_id].append(sport)
    return callback


async def distribute(callback):
    user_id = callback.from_user.id
    option = users[user_id][0]
    sport = users[user_id][-1]

    if option == 'news':
        await print_news(sport, callback)

    elif option == 'search_directory':
        if sport == 'hockey':
            await callback.message.edit_text(text=text.select, reply_markup=kb.type_statik)
        else:
            await callback.message.edit_text(
                text='Извините, данная функция находится в разработке⚡⚡⚡\nСейчас работает поиск по Хоккею!',
                reply_markup=kb.back)

    elif option == 'alerts':
        if user_id in users_news:
            pass
        else:
            users_news[user_id] = [False, False, False]
        if sport == 'football':
            users_news[user_id][0] = not users_news[user_id][0]
        elif sport == 'hockey':
            users_news[user_id][1] = not users_news[user_id][1]
        elif sport == 'volleyball':
            users_news[user_id][2] = not users_news[user_id][2]
        if sport == 'football':
            if users_news[user_id][0]:
                await callback.answer('🔔🔔🔔\nУведомления по футболу включены!', show_alert=True)
            else:
                await callback.answer('🔕🔕🔕\nУведомления по футболу выключены!', show_alert=True)
        elif sport == 'hockey':
            if users_news[user_id][1]:
                await callback.answer('🔔🔔🔔\nУведомления по хоккею включены!', show_alert=True)
            else:
                await callback.answer('🔕🔕🔕\nУведомления по хоккею выключены!', show_alert=True)
        elif sport == 'volleyball':
            if users_news[user_id][2]:
                await callback.answer('🔔🔔🔔\nУведомления по волейболу включены!', show_alert=True)
            else:
                await callback.answer('🔕🔕🔕\nУведомления по волейболу выключены!', show_alert=True)
        await alerts2.send_alert_news(callback, users_news)


@router.message()
async def process_name(message: Message):
    user_id = message.from_user.id
    user_text = message.text
    print(users)
    print(user_text)
    try:
        users_input[user_id][0] = user_text
        msg = await print_stat(message)
        users_input[user_id].append(msg)
        await bot.delete_message(chat_id=user_id, message_id=(users_input[user_id][-1]) - 2)
        await bot.delete_message(chat_id=user_id, message_id=(users_input[user_id][-1]) - 1)
    except:
        await message.answer(text='Я не знаю такой команды!',reply_markup=kb.go_menu)
async def print_news(sport, callback):
    sport_parsers = {
        'football': parsers.parser_football,
        'hockey': parsers.parser_hockey,
        'volleyball': parsers.parser_volleyball}
    post_text = sport_parsers[sport]()
    await callback.message.edit_text(text=post_text, reply_markup=kb.back)
