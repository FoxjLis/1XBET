import sqlite3 as sq

def match_history_between_teams(team_1, team_2):
    with sq.connect('sports.db') as con:
        text = ''
        cur = con.cursor()
        match_counter = 0
        cur.execute(f"SELECT * FROM matches WHERE Teams = '{team_1} – {team_2}' or Teams = '{team_2} – {team_1}'")
        for result in cur:
            match_counter += 1
            text += (f'✅ Матч проходил: {result[1]}\nТип противостояния: {result[2]}\nРезультат: {result[4]} {result[5]}\n\n')
        if text!="":
            text += (f'Всего матчей между командами: {match_counter}\n\n')
        return text

def player_stat(player_name):
    text = ''
    with sq.connect('sports.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM players WHERE name = '{player_name}'")
        for result in cur:
            if result[2] == 'В':
                text += (
                    f'Статистика игрока<b> {player_name}✅</b>\n<b>Позиция -</b> Вратарь\n<b>Игр сыграно - </b>{result[4]}\n<b>Бросков по его воротам совершено -</b> {result[5]}\n<b>Шайб пропущено -</b> {str(result[6])[1:]}\n<b>Процент отбитых шайб - </b>{result[7]}\n<b>Коэффицент надёжности -</b> {result[8]}\n<b>Игровое время</b> - {result[9]}\n<b>Штрафное время</b> - {result[10]}')
            elif result[2] == 'Н':
                text += (
                    f'Статистика игрока <b>{player_name}✅</b>\n<b>Позиция -</b> Нападающий\n<b>Очки -</b> {result[11]}\n<b>Заброшенные шайбы</b> - {result[12]}\n<b>Голевых передач отдано - </b>{result[13]}\n<b>Игр сыграно -</b> {result[14]}\n<b>Полезность в шайбах</b> - {result[15]}\n<b>Штрафное время</b> - {result[16]}\n<b>Бросков по воротам</b> - {result[17]}\n<b>Процент реализованных бросков - </b>{result[18]}\n<b>Среднее время на площадке за игру -</b> {result[19]}')
            else:
                text += (
                    f'Статистика игрока <b>{player_name}✅</b>\n<b>Позиция - Защитник\n<b>Очки</b> - {result[11]}\n<b>Заброшенные шайбы</b> - {result[12]}\n<b>Голевых передач отдано</b> - {result[13]}\n<b>Игр сыграно</b> - {result[14]}\n<b>Полезность в шайбах</b> - {result[15]}\n<b>Штрафное время</b> - {result[16]}\n<b>Бросков по воротам</b> - {result[17]}\n<b>Процент реализованных бросков</b> - {result[18]}\n<b>Среднее время на площадке за игру</b> - {result[19]}')
    return text

def team_members(team_name):
    text = ''
    with sq.connect('sports.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT TeamID FROM teams WHERE TeamName = '{team_name}'")
        team_name_value = cur.fetchall()[0][0]
        cur = con.cursor()
        cur.execute(f"SELECT name FROM players WHERE teamID = '{team_name_value}'")
        team = ''
        for result in cur:
            result = str(result).strip("(,)'")
            team += f'{result}, '
        text += (f'Состав команды {team_name} ✅\n{team}')
    return text

def team_stat(team_name):
    text = ''
    with sq.connect('sports.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM Teams WHERE TeamName = '{team_name}'")
        for result in cur:
            text += (
                f'Статистика команды {team_name} ✅\nТурниров, проводимых с участием команды - {result[4]}\nИгр сыграно - {result[5]}\nПобед - {result[6]}\nНичьих - {result[7]}\nПоражений - {result[8]}\nШайб забито - {result[9]}\nШайб пропущено - {result[10]}\nРазница забитых и пропущенных - {result[11]}\nНабранные очки - {result[12]}\nПроцент реализованных очков от возможных - {result[13]}')
    return text
