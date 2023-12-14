from aiogram import F, Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from Requests import (
    match_history_between_teams,
    player_stat,
    team_members,
    team_stat)
import alerts2
import text
from entertainment import matches_info
from calc_Elo_game import check_winner
from random import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import kb
from calculator_Elo import predict_matches
from alerts2 import send_last_news
import asyncio

news_set_volley = set()
news_set_foot = set()
news_set_hockey = set()

router = Router()
users = dict()
users_input = dict()
users_news = dict()
team_fight_history = dict()
users_points = dict()
bot_points = dict()
users_cvest = dict()


@router.message(Command("start"))
async def start_handler(msg: Message):
    message1 = await msg.answer(text='start...', reply_markup=types.ReplyKeyboardRemove())
    await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=message1.message_id)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
    await alerts2.send_alert_news()


@router.callback_query(F.data == 'menu')
async def news(callback: CallbackQuery):
    user_id = callback.from_user.id
    users[user_id] = []
    await callback.message.edit_text(text=text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == 'back')
async def news_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    options = ['search_directory', 'news', 'alerts',"prediction"]
    if users[user_id][-2] in options:
        await select_an_option(callback, users[user_id][-2])
        users[user_id] = [users[user_id][0]]
    elif users[user_id][0] == 'prediction':
        await distribute(callback)
    elif users[user_id][-3] == 'search_directory':
        users[user_id] = users[user_id][:-1:]
        await distribute(callback)


async def select_an_option(callback: CallbackQuery, category: str):
    user_id = callback.from_user.id
    users[user_id] = [category]
    await callback.message.edit_text(text='🏆 Выберите вид спорта', reply_markup=kb.kinds_sports)


@router.callback_query(F.data.in_(['news', 'alerts', 'search_directory', 'prediction']))
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
        await callback.message.edit_text(
            text='🔎 Введите Название команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
    elif callback.data == 'history':
        await callback.message.edit_text(
            text='🔎 Введите название первой команды c <b>заглавной буквы и город</b>, за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
        team_fight_history[user_id] = []


async def print_stat(message):
    user_id = message.from_user.id
    if users[user_id][-1] == 'player':
        if player_stat(users_input[user_id][0]) != '':
            await message.answer(text=player_stat(users_input[user_id][0]), reply_markup=kb.back)
        else:
            await message.answer(
                'Игрок с таким именем не найден ❌ Попробуйте ещё раз!\nВведите Фамилию и имя игрока <b>через пробел</b> с <b>заглавной буквы</b>\nПример: "Мишуров Андрей"',
                reply_markup=kb.back)

    if users[user_id][-1] == 'team':
        text_user = users_input[user_id][0]
        team_name = text_user[0:text_user.rfind(' ')]
        town_name = text_user[text_user.rfind(' ') + 1:]
        print(team_name)
        print(town_name)
        if team_stat(team_name, town_name) != '':
            stat = team_stat(team_name, town_name)
            members = team_members(team_name)
            await message.answer(text=f'{members}\n\n{stat}', reply_markup=kb.back)
        else:
            await message.answer(
                'Команда с таким названием или городом не найдена ❌ Попробуйте ещё раз! Введите Название команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
                reply_markup=kb.back)

    if users[user_id][-1] == 'history':
        team1 = users_input[user_id][0]
        team_name = team1[0:team1.rfind(' ')]
        town_name = team1[team1.rfind(' ') + 1:]
        if team_fight_history[user_id] == []:
            team_fight_history[user_id].append(team1)
            if team_stat(team_name, town_name) != "":
                await message.answer(
                    f'Первая команда - {team1} ✅\nВведите название второй команды, например: "Ак Барс Казань"',
                    reply_markup=kb.back)
            else:
                team_fight_history[user_id] = []
                await message.answer(
                    f'Команда с таким названием или городом не найдена ❌ Попробуйте ещё раз! Введите Название <b><i>первой</i></b> команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
                    reply_markup=kb.back)

        else:
            if team_stat(team_name, town_name) != "":
                team_fight_history[user_id].append(team1)
                text = match_history_between_teams(team_fight_history[user_id][0], team_fight_history[user_id][1])
                if text == '' or team_fight_history[user_id][0] == team_fight_history[user_id][1]:
                    text1 = 'не найдена ❌ Попробуйте ещё раз! Введите название первой команды'
                else:
                    text1 = 'найдена ✅'
                await message.answer(
                    text=f'История противостояний команд {team_fight_history[user_id][0]} и {team_fight_history[user_id][1]} {text1}\n\n{text}',
                    reply_markup=kb.back)
                team_fight_history[user_id] = []
            else:
                await message.answer(
                    f'Команда с таким названием или городом не найдена ❌ Попробуйте ещё раз! Введите Название <b><i>второй</i></b> команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
                    reply_markup=kb.back)


@router.callback_query(F.data.in_(['play', 'match_results']))
async def make_a_choice(callback: CallbackQuery):
    if callback.data == 'play':
        await entertainment_function(callback)
    elif callback.data == 'match_results':
        print(users)
        edit_text = await predict_matches()
        await callback.message.edit_text(text=edit_text, reply_markup=kb.back)


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
    elif option == 'prediction':
        if sport == 'hockey':
            await callback.message.edit_text(
                text='<b>Выберите Развлекательную функцию!</b>\n🔹<b>Игра</b> - соревнуйтесь с машиной в предсказании исходов последних матчей!\n🔹<b>Предсказание</b> - узнайте, какие команды выйграют по мнению бота в предстоящих матчах! ',
                reply_markup=kb.choose)
        else:
            await callback.message.edit_text(
                text='Извините, данная функция находится в разработке⚡⚡⚡\nСейчас работает функция по Хоккею!',
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
    try:
        user_id = message.from_user.id
        user_text = message.text
        users_input[user_id] = [0]
        users_input[user_id][0] = user_text
        if users[user_id][0] == "search_directory":
            await print_stat(message)
        elif users[user_id][0] == "prediction":
            await enter2(message)
    except:
        await message.answer(text=f'Я вас не понимаю!\nПожалуйста используйте кнопки!', reply_markup=kb.go_menu)
        message1 = await message.answer(text='Исправление ошибок...', reply_markup=types.ReplyKeyboardRemove())
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message1.message_id)


async def print_news(sport, callback):
    post_text = await send_last_news(sport)
    await asyncio.sleep(0.4)
    await callback.message.edit_text(text=post_text[-1], reply_markup=kb.back)


async def entertainment_function(callback):
    users_cvest[callback.from_user.id] = 0
    users_points[callback.from_user.id] = 0
    bot_points[callback.from_user.id] = 0
    question_number = users_cvest[callback.from_user.id]

    if question_number == 0:
        team1 = matches_info[question_number][0]
        team2 = matches_info[question_number][1]
        keyboard = [
            [KeyboardButton(text=team1)],
            [KeyboardButton(text=team2)]]
        keyboard1 = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await callback.message.edit_text(
            text='Готовы посоревноваться в прогнозировании результатов матчей с нашим ботом?\nБез лишних слов начнём🚀🚀🚀')
        await callback.message.answer(
            text=f'Первые на очереди у нас <b>{matches_info[question_number][0]}</b> и <b>{matches_info[question_number][1]}</b>\nКто по вашему мнению победит?',
            reply_markup=keyboard1)


async def enter2(message):
    user_id = message.from_user.id

    async def next_team(text):
        team1 = matches_info[users_cvest[message.from_user.id]][0]
        team2 = matches_info[users_cvest[message.from_user.id]][1]
        keyboard = [
            [KeyboardButton(text=team1)],
            [KeyboardButton(text=team2)]]
        keyboard1 = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        prefix_random = randint(0, 3)
        await message.answer(
            text=f'{text}\n{variants_of_start[prefix_random]} между <b>{matches_info[users_cvest[message.from_user.id]][0]}</b> и <b>{matches_info[users_cvest[message.from_user.id]][1]}</b>\nКто по вашему мнению победит?',
            reply_markup=keyboard1)

    variants_of_start = ['И следующий матч', 'И теперь у нас матч', 'Переходим к следующему матчу',
                         'А сейчас у нас матч']

    async def print_win():
        result_text = ''
        text = f'<b>Итак, подведём итоги</b>⚡⚡⚡\nВы угадали результатов матчей: <b>{users_points[user_id]}</b>\nБот угадал результатов матчей: <b>{bot_points[user_id]}</b>'
        if bot_points[user_id] > users_points[user_id]:
            result_text += ' \nВидимо наш бот и вправду неплох🤖'
        elif bot_points[user_id] == users_points[user_id]:
            result_text += ' \nВы оказались на равных с машиной, похвально\n🏅🏅🏅'
        else:
            result_text += ' \nНевероятно, у вас случаем нет экстрасенсорных способностей?🤯🤯🤯'
        await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(text=result_text, reply_markup=kb.go_menu)

    player_input = message.text
    print(users_cvest)
    print(matches_info[users_cvest[message.from_user.id]][2])
    if users_cvest[message.from_user.id] <= 5:
        if player_input == matches_info[users_cvest[message.from_user.id]][2]:
            text = 'Вы угадали✅'
            users_points[user_id] += 1
        else:
            text = 'Упс, немного ошиблись❌'
        if check_winner(matches_info[users_cvest[message.from_user.id]][0],
                        matches_info[users_cvest[message.from_user.id]][1]) == \
                matches_info[users_cvest[message.from_user.id]][2]:
            bot_points[user_id] += 1
        users_cvest[message.from_user.id] += 1
        if users_cvest[message.from_user.id] < 5:
            await next_team(text)
        else:
            await print_win()
