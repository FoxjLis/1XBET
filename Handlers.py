from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from Funk.calculator_Elo import predict_matches
from Funk.main_funk import users, sport_choice, run_selected_function, add_a_sport, team_fight_history, start_game, \
    play_game, users_input, print_statistics
from handlers import text, kb

router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message) -> None:
    message1 = await msg.answer(text='start...', reply_markup=types.ReplyKeyboardRemove())
    await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=message1.message_id)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.callback_query(F.data == 'menu')
async def menu_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    users[user_id] = []
    await callback.message.edit_text(text=text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == 'back')
async def news_callback_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    options = ['search_directory', 'news', 'alerts', "prediction"]
    if users[user_id][-2] in options:
        await sport_choice(callback, users[user_id][-2])
        users[user_id] = [users[user_id][0]]
    elif users[user_id][-3] == 'search_directory':
        users[user_id] = users[user_id][:-1:]
        await run_selected_function(callback)


@router.callback_query(F.data.in_(['news', 'alerts', 'search_directory', 'prediction']))
async def news_callback_handler(callback: CallbackQuery) -> None:
    await sport_choice(callback, callback.data)


@router.callback_query(F.data.in_(['football', 'hockey', 'volleyball']))
async def select_function_handler(callback: CallbackQuery) -> None:
    await run_selected_function(await add_a_sport(callback))


@router.callback_query(F.data.in_(['player', 'team', 'history']))
async def select_type_statistics_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    users[user_id].append(callback.data)
    if callback.data == 'player':
        await callback.message.edit_text(
            text='🔎 Введите Фамилию и имя игрока <b>через пробел</b> с '
                 '<b>заглавной буквы</b>\nПример: "Мишуров Андрей"',
            reply_markup=kb.back)
    elif callback.data == 'team':
        await callback.message.edit_text(
            text='🔎 Введите название первой команды c <b>заглавной буквы и город</b>, '
                 'за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
    elif callback.data == 'history':
        await callback.message.edit_text(
            text='🔎 Введите название первой команды c <b>заглавной буквы и город</b>, '
                 'за который она выступает, например: "ЦСКА Москва"',
            reply_markup=kb.back)
        team_fight_history[user_id] = []


@router.callback_query(F.data.in_(['play', 'match_results']))
async def make_choice_stat_handler(callback: CallbackQuery) -> None:
    if callback.data == 'play':
        await start_game(callback)
    elif callback.data == 'match_results':
        edit_text = await predict_matches()
        await callback.message.edit_text(text=edit_text, reply_markup=kb.back)


@router.message()
async def process_message_handler(message: Message) -> None:
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
