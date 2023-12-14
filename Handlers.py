from aiogram import F, Router, types
from aiogram.filters import Command
from Funk.game_func import get_last_5_matches
from Funk.game_func import check_winner
from random import randint
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, Message
from Funk.calculator_Elo import predict_matches
from Funk.statistics_func import (
    match_history_between_teams,
    player_stat,
    team_members,
    team_stat)
from Funk import News_func
from handlers import text, kb
import asyncio

router = Router()

users = dict()
users_input = dict()
users_news = dict()
team_fight_history = dict()
users_game = dict()
users_points = dict()
bot_points = dict()
users_cvest = dict()


@router.message(Command("start"))
async def start_handler(msg: Message) -> None:
    message1 = await msg.answer(text='start...', reply_markup=types.ReplyKeyboardRemove())
    await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=message1.message_id)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.callback_query(F.data == 'menu')
async def news(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    users[user_id] = []
    await callback.message.edit_text(text=text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == 'back')
async def news_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    options = ['search_directory', 'news', 'alerts', "prediction"]
    if users[user_id][-2] in options:
        await select_an_option(callback, users[user_id][-2])
        users[user_id] = [users[user_id][0]]
    elif users[user_id][-3] == 'search_directory':
        users[user_id] = users[user_id][:-1:]
        await distribute(callback)


async def select_an_option(callback: CallbackQuery, category: str) -> None:
    user_id = callback.from_user.id
    users[user_id] = [category]
    await callback.message.edit_text(text='🏆 Выберите вид спорта', reply_markup=kb.kinds_sports)


@router.callback_query(F.data.in_(['news', 'alerts', 'search_directory', 'prediction']))
async def news_callback(callback: CallbackQuery) -> None:
    await select_an_option(callback, callback.data)


@router.callback_query(F.data.in_(['football', 'hockey', 'volleyball']))
async def sport_news(callback: CallbackQuery) -> None:
    await distribute(await add_a_sport(callback))


@router.callback_query(F.data.in_(['player', 'team', 'history']))
async def type_stat(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    users[user_id].append(callback.data)
    if callback.data == 'player':
        await callback.message.edit_text(
            text='🔎 Введите Фамилию и имя игрока <b>через пробел</b> с '
                 '<b>заглавной буквы</b>\nПример: "Мишуров Андрей"',
            reply_markup=kb.back)
    elif callback.data == 'team':
        await callback.message.edit_text(
            text='🔎 Введите Название команды c заглавной буквы и город, '
                 'за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
    elif callback.data == 'history':
        await callback.message.edit_text(
            text='🔎 Введите название первой команды c <b>заглавной буквы и город</b>, '
                 'за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
        team_fight_history[user_id] = []


async def print_statistics(message: Message) -> None:
    user_id = message.from_user.id
    if users[user_id][-1] == 'player':
        if player_stat(users_input[user_id][0]) != '':
            await message.answer(text=player_stat(users_input[user_id][0]), reply_markup=kb.back)
        else:
            await message.answer(
                'Игрок с таким именем не найден ❌ Попробуйте ещё раз!\n'
                'Введите Фамилию и имя игрока <b>через пробел</b> с <b>заглавной буквы</b>'
                '\nПример: "Мишуров Андрей"',
                reply_markup=kb.back)

    if users[user_id][-1] == 'team':
        text_user = users_input[user_id][0]
        team_name = text_user[0:text_user.rfind(' ')]
        town_name = text_user[text_user.rfind(' ') + 1:]
        if team_stat(team_name, town_name) != '':
            stat = team_stat(team_name, town_name)
            members = team_members(team_name)
            await message.answer(text=f'{members}\n\n{stat}', reply_markup=kb.back)
        else:
            await message.answer(
                'Команда с таким названием или городом не найдена ❌ Попробуйте ещё раз! '
                'Введите Название команды c заглавной буквы и город, за который она выступает, '
                'например: "ЦСКА Москва"',
                reply_markup=kb.back)

    if users[user_id][-1] == 'history':
        team1 = users_input[user_id][0]
        team_name = team1[0:team1.rfind(' ')]
        town_name = team1[team1.rfind(' ') + 1:]
        if not team_fight_history[user_id]:
            team_fight_history[user_id].append(team1)
            if team_stat(team_name, town_name) != "":
                await message.answer(
                    f'Первая команда - {team1} ✅\nВведите название'
                    f' второй команды, например: "Ак Барс Казань"',
                    reply_markup=kb.back)
            else:
                team_fight_history[user_id] = []
                await message.answer(
                    f'Команда с таким названием или городом не найдена ❌'
                    f' Попробуйте ещё раз! Введите Название <b><i>первой</i></b>'
                    f' команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
                    reply_markup=kb.back)

        else:
            if team_stat(team_name, town_name) != "":
                team_fight_history[user_id].append(team1)
                text_team_stat = match_history_between_teams(team_fight_history[user_id][0],
                                                             team_fight_history[user_id][1])
                if text_team_stat == '' or team_fight_history[user_id][0] == team_fight_history[user_id][1]:
                    text_find = 'не найдена ❌ Попробуйте ещё раз! Введите название первой команды'
                else:
                    text_find = 'найдена ✅'
                await message.answer(
                    text=f'История противостояний команд {team_fight_history[user_id][0]}'
                         f' и {team_fight_history[user_id][1]} {text_find}\n\n{text_team_stat}',
                    reply_markup=kb.back)
                team_fight_history[user_id] = []
            else:
                await message.answer(
                    f'Команда с таким названием или городом не найдена ❌'
                    f' Попробуйте ещё раз! Введите Название <b><i>второй</i></b>'
                    f' команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
                    reply_markup=kb.back)


@router.callback_query(F.data.in_(['play', 'match_results']))
async def make_a_choice(callback: CallbackQuery) -> None:
    if callback.data == 'play':
        await start_game(callback)
    elif callback.data == 'match_results':
        edit_text = await predict_matches()
        await callback.message.edit_text(text=edit_text, reply_markup=kb.back)


async def add_a_sport(callback: CallbackQuery) -> CallbackQuery:
    sport = callback.data
    user_id = callback.from_user.id
    users[user_id].append(sport)
    return callback


async def distribute(callback: CallbackQuery) -> None:
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
                text='<b>Выберите Развлекательную функцию!</b>\n🔹<b>Игра</b> - '
                     'соревнуйтесь с машиной в предсказании исходов последних матчей!\n'
                     '🔹<b>Предсказание</b> - узнайте, какие команды выйграют по мнению бота в предстоящих матчах! ',
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


@router.message()
async def process_name(message: Message) -> None:
    try:
        user_id = message.from_user.id
        user_text = message.text
        users_input[user_id] = [0]
        users_input[user_id][0] = user_text
        if users[user_id][0] == "search_directory":
            await print_statistics(message)
        elif users[user_id][0] == "prediction":
            await play_game(message)
    except LookupError:
        await message.answer(text=f'Я вас не понимаю!\nПожалуйста используйте кнопки!', reply_markup=kb.go_menu)
        message1 = await message.answer(text='Исправление ошибок...', reply_markup=types.ReplyKeyboardRemove())
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message1.message_id)


async def print_news(sport: str, callback: CallbackQuery) -> None:
    post_text = await News_func.send_last_news(sport)
    await asyncio.sleep(0.4)
    await callback.message.edit_text(text=post_text[-1], reply_markup=kb.back)


async def start_game(callback: CallbackQuery) -> None:
    users_cvest[callback.from_user.id] = 0
    users_points[callback.from_user.id] = 0
    bot_points[callback.from_user.id] = 0
    matches_info = get_last_5_matches()
    question_number = users_cvest[callback.from_user.id]
    if question_number == 0:
        team1 = matches_info[question_number][0]
        team2 = matches_info[question_number][1]
        keyboard = [
            [KeyboardButton(text=team1)],
            [KeyboardButton(text=team2)]]
        keyboard1 = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await callback.message.edit_text(
            text='Готовы посоревноваться в прогнозировании результатов матчей с нашим ботом?\n'
                 'Без лишних слов начнём🚀🚀🚀')
        await callback.message.answer(
            text=f'Первые на очереди у нас <b>{matches_info[question_number][0]}</b>'
                 f' и <b>{matches_info[question_number][1]}</b>\nКто по вашему мнению победит?',
            reply_markup=keyboard1)


async def play_game(message: Message) -> None:
    user_id = message.from_user.id
    matches_info = get_last_5_matches()

    async def next_team(text_user_guessed: str) -> None:
        team1 = matches_info[users_cvest[message.from_user.id]][0]
        team2 = matches_info[users_cvest[message.from_user.id]][1]
        keyboard = [
            [KeyboardButton(text=team1)],
            [KeyboardButton(text=team2)]]
        keyboard1 = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        prefix_random = randint(0, 3)
        await message.answer(
            text=f'{text_user_guessed}\n{variants_of_start[prefix_random]} '
                 f'между <b>{matches_info[users_cvest[message.from_user.id]][0]}</b> и '
                 f'<b>{matches_info[users_cvest[message.from_user.id]][1]}</b>\nКто по вашему мнению победит?',
            reply_markup=keyboard1)

    variants_of_start = ['И следующий матч', 'И теперь у нас матч', 'Переходим к следующему матчу',
                         'А сейчас у нас матч']

    async def print_win():
        final_text = ''
        text_results = (f'<b>Итак, подведём итоги</b>⚡⚡⚡\nВы угадали результатов матчей:'
                        f' <b>{users_points[user_id]}</b>\nБот угадал результатов матчей: <b>{bot_points[user_id]}</b>')
        if bot_points[user_id] > users_points[user_id]:
            final_text += ' \nВидимо наш бот и вправду неплох🤖'
        elif bot_points[user_id] == users_points[user_id]:
            final_text += ' \nВы оказались на равных с машиной, похвально\n🏅🏅🏅'
        else:
            final_text += ' \nНевероятно, у вас случаем нет экстрасенсорных способностей?🤯🤯🤯'
        await message.answer(text=text_results, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(text=final_text, reply_markup=kb.go_menu)

    player_input = message.text
    if users_cvest[message.from_user.id] <= 5:
        if player_input == matches_info[users_cvest[message.from_user.id]][2]:
            text_guessed = 'Вы угадали✅'
            users_points[user_id] += 1
        else:
            text_guessed = 'Упс, немного ошиблись❌'
        if check_winner(matches_info[users_cvest[message.from_user.id]][0],
                        matches_info[users_cvest[message.from_user.id]][1]) == \
                matches_info[users_cvest[message.from_user.id]][2]:
            bot_points[user_id] += 1
        users_cvest[message.from_user.id] += 1
        if users_cvest[message.from_user.id] < 5:
            await next_team(text_guessed)
        else:
            await print_win()
