import sqlite3
from datetime import *
from random import *

initial_elo = 1200


def calculate_team_elo():
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    today = date.today()
    current_date = today.strftime('%Y-%m-%d')

    # Получение первых 50 строк из таблицы matches
    cursor.execute("SELECT teams, score FROM matches where score != '–:–'")
    matches_data = cursor.fetchall()

    # Начальные значения ELO для каждой команды
    K = 40

    # Словарь для хранения рейтинга команд с использованием полных названий
    team_elo_dict = {}

    # Получаем уникальные названия команд и добавляем их в словарь
    for match in matches_data:
        teams = match[0].split(' – ')
        team1, team2 = teams[0], teams[1]

        # Проверяем, есть ли команда в словаре, и если нет, добавляем ее с начальным ELO
        if team1 not in team_elo_dict:
            team_elo_dict[team1] = initial_elo
        if team2 not in team_elo_dict:
            team_elo_dict[team2] = initial_elo

    # Функция для вычисления нового рейтинга команды (остается без изменений)
    def calculate_elo(Ro, Ropp, S, K):
        E = 1 / (1 + 10 ** ((Ropp - Ro) / 400))
        Rn = Ro + K * (S - E)
        return Rn

    # Рассчитываем ELO для каждой команды на основе результатов матчей (с обработкой результата)
    win_streaks = {team: 0 for team in team_elo_dict}
    lose_streaks = {team: 0 for team in team_elo_dict}

    # Рассчитываем ELO для каждой команды на основе результатов матчей
    for match in matches_data:
        teams = match[0].split(' – ')
        team1, team2 = teams[0], teams[1]
        score = match[1].split(':')
        team1_score, team2_score = int(score[0]), int(score[1].split()[0])  # Изменено для учета ОТ/Б

        Ro1, Ro2 = team_elo_dict[team1], team_elo_dict[team2]
        E1, E2 = 1 / (1 + 10 ** ((Ro2 - Ro1) / 400)), 1 / (1 + 10 ** ((Ro1 - Ro2) / 400))

        S1 = 1 if team1_score > team2_score else 0 if team1_score < team2_score else 0.5
        S2 = 1 - S1

        # Учет дополнительных обозначений в счете при расчете ELO
        is_overtime = 'ОТ' in match[1]
        is_shootout = 'Б' in match[1]

        if is_overtime:
            if S1 > S2:
                S1, S2 = 0.75, 0.25
            elif S1 < S2:
                S1, S2 = 0.25, 0.75
            else:
                S1, S2 = 0.5, 0.5
        elif is_shootout:
            if S1 > S2:
                S1, S2 = 0.6, 0.4
            elif S1 < S2:
                S1, S2 = 0.4, 0.6
            else:
                S1, S2 = 0.5, 0.5

        # Обновление серии побед и поражений для каждой команды
        if S1 == 1:
            win_streaks[team1] += 1
            lose_streaks[team2] = 0
            if win_streaks[team1] >= 3:
                K += 2
        elif S2 == 1:
            win_streaks[team2] += 1
            lose_streaks[team1] = 0
            if win_streaks[team2] >= 3:
                K += 2
        else:
            win_streaks[team1] = 0
            win_streaks[team2] = 0
            lose_streaks[team1] += 1
            lose_streaks[team2] += 1

            if lose_streaks[team1] >= 3:
                K -= 2
            elif lose_streaks[team1] < 3 and K != 40:
                K = 40

            if lose_streaks[team2] >= 3:
                K -= 2
            elif lose_streaks[team2] < 3 and K != 40:
                K = 40

        Rn1 = calculate_elo(Ro1, Ro2, S1, K)
        Rn2 = calculate_elo(Ro2, Ro1, S2, K)

        team_elo_dict[team1] = Rn1
        team_elo_dict[team2] = Rn2

    return team_elo_dict


def display_matches(team_elo_dict):
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    today = date.today()
    current_date = today.strftime('%Y-%m-%d')

    cursor.execute("SELECT teams, matchdate FROM matches WHERE SUBSTR(matchdate, 1, 10) = ? ORDER BY matchdate ASC",
                   (current_date,))
    todays_matches = cursor.fetchall()

    if todays_matches:
        print(f"Матчи на сегодня ({current_date}):")
        for match in todays_matches:
            teams, match_date_time = match[0], match[1]
            match_date, match_time = match_date_time.split(', ')

            team1, team2 = teams.split(' – ')
            elo_team1 = team_elo_dict.get(team1, initial_elo)
            elo_team2 = team_elo_dict.get(team2, initial_elo)

            if elo_team1 > elo_team2:
                print(f"Команды: {team1} <-|-> {team2} (Победит: {team1}), Дата: {match_date}, Время: {match_time}")
            else:
                print(f"Команды: {team1} <-|-> {team2} (Победит: {team2}), Дата: {match_date}, Время: {match_time}")
    else:
        cursor.execute("SELECT DISTINCT matchdate FROM matches WHERE matchdate > ? ORDER BY matchdate ASC",
                       (current_date,))
        nearest_date_match = cursor.fetchone()

        if nearest_date_match:
            nearest_date = nearest_date_match[0].split(', ')[0]
            print(f"Ближайшие матчи ({nearest_date}):")
            cursor.execute(
                "SELECT teams, matchdate FROM matches WHERE SUBSTR(matchdate, 1, 10) = ? ORDER BY matchdate ASC",
                (nearest_date,))
            nearest_matches = cursor.fetchall()

            for match in nearest_matches:
                teams, match_date_time = match[0], match[1]
                match_date, match_time = match_date_time.split(', ')

                team1, team2 = teams.split(' – ')
                elo_team1 = team_elo_dict.get(team1, initial_elo)
                elo_team2 = team_elo_dict.get(team2, initial_elo)

                if elo_team1 > elo_team2:
                    print(f"Команды: {team1} <-|-> {team2} (Победит: {team1}), Дата: {match_date}, Время: {match_time}")
                else:
                    print(f"Команды: {team1} <-|-> {team2} (Победит: {team2}), Дата: {match_date}, Время: {match_time}")
        else:
            print("На ближайшее время матчи не найдены.")

        conn.close()


def get_last_5_matches():
    last_5_matches = []
    current_date = datetime.now()

    with sqlite3.connect('sports.db') as con:
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


def entertainment_function():
    team_elo = calculate_team_elo()

    player_score = 0
    bot_score = 0
    print('Готовы посоревноваться в прогнозировании результатов матчей с нашим ботом?\nБез лишних слов начнём')
    variants_of_start = ['И следующий матч', 'И теперь у нас матч', 'Переходим к следующему матчу',
                         'А сейчас у нас матч']

    for question_number in range(5):
        if question_number == 0:
            print(
                f'Первые на очереди у нас {matches_info[question_number][0]} и {matches_info[question_number][1]}. Кто по вашему мнению победит?')

            player_input = input()

            if player_input == matches_info[question_number][2]:
                print('Вы угадали!')
                player_score += 1
            else:
                print('Упс, немного ошиблись')
                team1_elo = team_elo.get(matches_info[question_number][0], 0)
                team2_elo = team_elo.get(matches_info[question_number][1], 0)
                max_elo = max(team1_elo,team2_elo)
                if matches_info[question_number][2] in team_elo and team_elo[matches_info[question_number][2]] == max_elo:
                    bot_score +=1
        else:
            prefix_random = randint(0, 4)
            print(
                f'{variants_of_start[prefix_random]} между {matches_info[question_number][0]} и {matches_info[question_number][1]}. Кто по вашему мнению победит?')

            player_input = input()

            if player_input == matches_info[question_number][2]:
                print('Вы угадали!')
                player_score += 1
            else:
                print('Упс, немного ошиблись')
                team1_elo = team_elo.get(matches_info[question_number][0], 0)
                team2_elo = team_elo.get(matches_info[question_number][1], 0)
                max_elo = max(team1_elo, team2_elo)
                if matches_info[question_number][2] in team_elo and team_elo[
                    matches_info[question_number][2]] == max_elo:
                    bot_score += 1

    result_text = f'Итак подведём итоги: вы угадали {player_score} результатов матчей, бот в свою очередь {bot_score}.'
    if bot_score > player_score:
        result_text += ' \nВидимо наш бот и вправду неплох'
    elif bot_score == player_score:
        result_text += ' \nВы оказались на равных с машиной, похвально.'
    else:
        result_text += ' \nНевероятно, у вас случаем нет экстрасенсорных способностей?'
    print(result_text)


display_matches(calculate_team_elo())
entertainment_function()