import sqlite3
from datetime import date


def get_last_5_matches() -> list:
    last_5_matches = []
    with sqlite3.connect('../Main/sports.db') as con:
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


def calculate_elo():
    text = ""
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('Main/sports.db')
    cursor = conn.cursor()

    today = date.today()
    current_date = today.strftime('%Y-%m-%d')

    # Получение первых 50 строк из таблицы matches
    cursor.execute("SELECT teams, score FROM matches where score != '–:–'")
    matches_data = cursor.fetchall()

    # Начальные значения ELO для каждой команды
    initial_elo = 1200
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
    conn.close()
    return team_elo_dict


teams_elo = (calculate_elo())


def check_winner(team1, team2):
    if teams_elo[team1] > teams_elo[team2]:
        return team1
    else:
        return team2
