import kb
from calc_Elo_game import check_winner
import sqlite3 as sq
from datetime import *
from random import *
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram import Bot
import config
bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML')


def get_last_5_matches():
    last_5_matches = []
    current_date = datetime.now()

    with sq.connect('sports.db') as con:
        cur = con.cursor()
        id_last_match = cur.execute(f"SELECT MatchID FROM matches WHERE score = '–:–' LIMIT 1")
        id_last_match = cur.fetchall()
        id_last_match = str(id_last_match[0])
        id_last_match = int(id_last_match.strip('(),'))

    for match_num in range(1, 6):
        match_teams_and_winner = []
        match_data = cur.execute(f"SELECT teams, score FROM matches WHERE MatchID = {id_last_match - match_num}")
        match_data = cur.fetchall()
        for match in match_data:
            teams = match[0].split(' – ')
            team1, team2 = teams[0], teams[1]
            score = match[1].split(':')
            score_team1, score_team2 = int(score[0]), int(score[1].strip('БОТ '))
            match_teams_and_winner.append(team1)
            match_teams_and_winner.append(team2)
            if score_team1 > score_team2:
                match_teams_and_winner.append(team1)
            else:
                match_teams_and_winner.append(team2)
            last_5_matches.append(match_teams_and_winner)
    return last_5_matches


matches_info = get_last_5_matches()  # содержит список последних 5 матчей, для каждого указаны участники и победитель
print(matches_info)

async def get_message():
    updates = await bot.get_updates()
    if updates:
        message = updates[0].message
        return message

async def entertainment_function(callback):
    player_score = 0
    bot_score = 0
    await callback.message.edit_text(
        text='Готовы посоревноваться в прогнозировании результатов матчей с нашим ботом?\nБез лишних слов начнём')
    variants_of_start = ['И следующий матч', 'И теперь у нас матч', 'Переходим к следующему матчу',
                         'А сейчас у нас матч']

    for question_number in range(5):
        if question_number == 0:
            team1 = matches_info[question_number][0]
            team2 = matches_info[question_number][1]
            keyboard = [
                [KeyboardButton(text=team1)],
                [KeyboardButton(text=team2)]]
            keyboard1 = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
            await callback.message.answer(text=
                                          f'Первые на очереди у нас {matches_info[question_number][0]} и {matches_info[question_number][1]}. Кто по вашему мнению победит?',
                                          reply_markup=keyboard1)
            message = await get_message()
            if message:
                print(message.text)

            player_input=123
            if player_input == matches_info[question_number][2]:
                print('Вы угадали!')
                player_score += 1
            else:
                print('Упс, немного ошиблись')
            if check_winner(matches_info[question_number][0], matches_info[question_number][1]) == \
                    matches_info[question_number][2]:
                bot_score += 1
        else:
            prefix_random = randint(0, 4)
            await callback.message.edit_text(text=
                                             f'{variants_of_start[prefix_random]} между {matches_info[question_number][0]} и {matches_info[question_number][1]}. Кто по вашему мнению победит?')

            player_input = input()

            if player_input == matches_info[question_number][2]:
                print('Вы угадали!')
                player_score += 1
            else:
                print('Упс, немного ошиблись')
            if check_winner(matches_info[question_number][0], matches_info[question_number][1]) == \
                    matches_info[question_number][2]:
                bot_score += 1

    result_text = f'Итак, подведём итоги: вы угадали {player_score} результатов матчей, бот в свою очередь {bot_score}.'
    if bot_score > player_score:
        result_text += ' \nВидимо наш бот и вправду неплох'
    elif bot_score == player_score:
        result_text += ' \nВы оказались на равных с машиной, похвально.'
    else:
        result_text += ' \nНевероятно, у вас случаем нет экстрасенсорных способностей?'
    await callback.message.edit_text(text=result_text, reply_markup=kb.go_menu)
