from aiogram import types
from Funk.game_func import get_last_5_matches
from Funk.game_func import check_winner
from random import randint
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, Message
from Funk.statistics_func import match_history_between_teams, player_stat, team_members, team_stat
from Funk import News_func
from handlers import text, kb
import asyncio
users = dict()
users_input = dict()
users_news = dict()
team_fight_history = dict()
users_game = dict()


async def print_news(sport: str, callback: CallbackQuery) -> None:
    post_text = await News_func.send_last_news(sport)
    await asyncio.sleep(0.4)
    await callback.message.edit_text(text=post_text[-1], reply_markup=kb.back)


async def sport_choice(callback: CallbackQuery, category: str) -> None:
    user_id = callback.from_user.id
    users[user_id] = [category]
    await callback.message.edit_text(text='🏆 Выберите вид спорта', reply_markup=kb.kinds_sports)


async def run_selected_function(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    option = users[user_id][0]
    sport = users[user_id][-1]
    if option == 'news':
        await print_news(sport, callback)

    elif option == 'search_directory':
        await select_static(callback, sport)

    elif option == 'prediction':
        await do_prediction(callback, sport)

    elif option == 'alerts':
        if user_id in users_news:
            pass
        else:
            users_news[user_id] = [False, False, False]  # 0-футбол #1-Хоккей #2-Волейбол
        await connect_alerts(callback, sport, user_id)


async def select_static(callback: CallbackQuery, sport: str) -> None:
    if sport == 'hockey':
        await callback.message.edit_text(text=text.select, reply_markup=kb.type_statik)
    else:
        await callback.message.edit_text(
            text='Извините, данная функция находится в разработке⚡⚡⚡\nСейчас работает поиск по Хоккею!',
            reply_markup=kb.back)


async def do_prediction(callback: CallbackQuery, sport: str) -> None:
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


async def connect_alerts(callback: CallbackQuery, sport: str, user_id: int) -> None:
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
    await News_func.do_parser_news(callback,users_news)


async def add_a_sport(callback: CallbackQuery) -> CallbackQuery:
    sport = callback.data
    user_id = callback.from_user.id
    users[user_id].append(sport)
    return callback


async def print_statistics(message: Message) -> None:
    user_id = message.from_user.id
    if users[user_id][-1] == 'player':
        await print_stat_player(message, user_id)

    if users[user_id][-1] == 'team':
        await print_stat_team(message, user_id)

    if users[user_id][-1] == 'history':
        await print_stat_history(message, user_id)


async def print_stat_player(message: Message, user_id: int) -> None:
    if player_stat(users_input[user_id][0]) != '':
        await message.answer(text=player_stat(users_input[user_id][0]), reply_markup=kb.back)
    else:
        await message.answer(
            'Игрок с таким именем не найден ❌ Попробуйте ещё раз!\n'
            'Введите Фамилию и имя игрока <b>через пробел</b> с <b>заглавной буквы</b>'
            '\nПример: "Мишуров Андрей"',
            reply_markup=kb.back)


async def print_stat_history(message: Message, user_id: int) -> None:
    team = users_input[user_id][0]
    team_name = team[0:team.rfind(' ')]
    town_name = team[team.rfind(' ') + 1:]
    if not team_fight_history[user_id]:
        team_fight_history[user_id].append(team)
        if team_stat(team_name, town_name) != "":
            await message.answer(
                f'Первая команда - {team} ✅\nВведите название'
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
            team1 = team_fight_history[user_id][0]
            team2 = team_fight_history[user_id][1]
            team_fight_history[user_id].append(team)
            text_team_stat = match_history_between_teams(team1, team2)
            if text_team_stat == '' or team1 == team2:
                text_find = 'не найдена ❌ Попробуйте ещё раз! Введите название первой команды'
            else:
                text_find = 'найдена ✅'
            await message.answer(
                text=f'История противостояний команд {team1}'
                     f' и {team2} {text_find}\n\n{text_team_stat}',
                reply_markup=kb.back)
            team_fight_history[user_id] = []
        else:
            await message.answer(
                f'Команда с таким названием или городом не найдена ❌'
                f' Попробуйте ещё раз! Введите Название <b><i>второй</i></b>'
                f' команды c заглавной буквы и город, за который она выступает, например: "ЦСКА Москва"',
                reply_markup=kb.back)


async def print_stat_team(message:Message, user_id:int) -> None:
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


async def start_game(callback: CallbackQuery) -> None:
    users_game[callback.from_user.id] = [0, 0, 0]  # 0-вопрос #1-очки игрока #2-очки Бота
    matches_info = get_last_5_matches()
    question_number = users_game[callback.from_user.id][0]
    if question_number == 0:
        team1 = matches_info[question_number][0]
        team2 = matches_info[question_number][1]
        keyboard = [
            [KeyboardButton(text=team1)],
            [KeyboardButton(text=team2)]]
        keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await callback.message.edit_text(
            text='Готовы посоревноваться в прогнозировании результатов матчей с нашим ботом?\n'
                 'Без лишних слов начнём🚀🚀🚀')
        await callback.message.answer(
            text=f'Первые на очереди у нас <b>{team1}</b>'
                 f' и <b>{team2}</b>\nКто по вашему мнению победит?',
            reply_markup=keyboard)


async def play_game(message: Message) -> None:
    matches_info = get_last_5_matches()
    team1 = matches_info[users_game[message.from_user.id][0]][0]
    team2 = matches_info[users_game[message.from_user.id][0]][1]
    team_win = matches_info[users_game[message.from_user.id][0]][2]
    bot_points = users_game[message.from_user.id][2]
    user_point = users_game[message.from_user.id][1]

    async def next_team(text_user_guessed: str) -> None:
        next_team1 = matches_info[users_game[message.from_user.id][0]][0]
        next_team2 = matches_info[users_game[message.from_user.id][0]][1]
        keyboard = [
            [KeyboardButton(text=next_team1)],
            [KeyboardButton(text=next_team2)]]
        keyboard1 = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        prefix_random = randint(0, 3)
        await message.answer(text=f'{text_user_guessed}\n{variants_of_start[prefix_random]}'
                                  f' между <b>{next_team1}</b> и <b>{next_team2}</b>\nКто по вашему мнению победит?',
                             reply_markup=keyboard1)

    variants_of_start = ['И следующий матч', 'И теперь у нас матч', 'Переходим к следующему матчу',
                         'А сейчас у нас матч']

    async def print_win() -> None:
        final_text = ''
        text_results = (f'<b>Итак, подведём итоги</b>⚡⚡⚡\nВы угадали результатов матчей:'
                        f' <b>{user_point}</b>\nБот угадал результатов матчей: <b>{bot_points}</b>')
        if bot_points > user_point:
            final_text += ' \nВидимо наш бот и вправду неплох🤖'
        elif bot_points == user_point:
            final_text += ' \nВы оказались на равных с машиной, похвально\n🏅🏅🏅'
        else:
            final_text += ' \nНевероятно, у вас случаем нет экстрасенсорных способностей?🤯🤯🤯'
        await message.answer(text=text_results, reply_markup=types.ReplyKeyboardRemove())
        await message.answer(text=final_text, reply_markup=kb.go_menu)

    player_input = message.text
    if users_game[message.from_user.id][0] <= 5:
        if player_input == team_win:
            text_guessed = 'Вы угадали✅'
            user_point += 1
        else:
            text_guessed = 'Упс, немного ошиблись❌'
        if check_winner(team1, team2) == team_win:
            bot_points += 1
        users_game[message.from_user.id][0] += 1
        if users_game[message.from_user.id][0] < 5:
            await next_team(text_guessed)
        else:
            await print_win()
    users_game[message.from_user.id][2] = bot_points
    users_game[message.from_user.id][1] = user_point
