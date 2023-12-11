import sqlite3
from datetime import date
async def predict_matches():
    text=""
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('sports.db')
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

    # Выполнение запроса для поиска матчей на текущую дату
    cursor.execute("SELECT teams, matchdate FROM matches WHERE SUBSTR(matchdate, 1, 10) = ? ORDER BY matchdate ASC",
                   (current_date,))
    todays_matches = cursor.fetchall()

    if todays_matches:
        # Если есть матчи на сегодня, выводим их
        text+=(f"Предположительный исход матчей сегодня ({current_date})✅")
        for match in todays_matches:
            teams, match_date_time = match[0], match[1]
            match_date, match_time = match_date_time.split(', ')

            team1, team2 = teams.split(' – ')
            elo_team1 = team_elo_dict.get(team1, initial_elo)
            elo_team2 = team_elo_dict.get(team2, initial_elo)

            if elo_team1 > elo_team2:
                text+=(f"🏒{match_time}\n {team1} - {team2}\n<b>Победит:</b> {team1}🏅\n\n")
            else:
                text+=(f"🏒{match_time}\n {team1} - {team2}\n<b>Победит:</b> {team2}🏅\n\n")
    else:
        # Если на сегодня нет матчей, ищем и выводим ближайшую дату с матчами
        cursor.execute("SELECT DISTINCT matchdate FROM matches WHERE matchdate > ? ORDER BY matchdate ASC",
                       (current_date,))
        nearest_date_match = cursor.fetchone()

        if nearest_date_match:
            # Если найдена ближайшая дата с матчами, выводим все матчи для этой даты
            nearest_date = nearest_date_match[0].split(', ')[0]  # Выделение только даты из строки
            text+=(f"Предположительный исход матчей {nearest_date} ✅\n\n")

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
                    text+=(f"🏒{match_time} {team1} - {team2}\n<b>Победит:</b> {team1}🏅\n\n")
                else:
                    text+=(f"🏒{match_time} {team1} - {team2}\n<b>Победит:</b> {team2}🏅\n\n")
        else:
            text+=("На ближайшее время матчи не найдены.")
    conn.close()
    return (text)
