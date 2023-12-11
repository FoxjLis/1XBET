from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
import text

menu = [[InlineKeyboardButton(text='Статистика', callback_data="search_directory")],
        [InlineKeyboardButton(text="🔍Новости", callback_data='news'),
         InlineKeyboardButton(text="🚀Оповещения", callback_data='alerts')],
        [InlineKeyboardButton(text="🥇Развлекательная функция", callback_data="prediction")]]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
kinds_sports = [
    [InlineKeyboardButton(text="Футбол", callback_data="football"),
     InlineKeyboardButton(text="Волейбол", callback_data="volleyball")],
    [InlineKeyboardButton(text="Хоккей", callback_data="hockey"),
     InlineKeyboardButton(text="В меню", callback_data="menu")]]
kinds_sports = InlineKeyboardMarkup(inline_keyboard=kinds_sports)

back = [
    [InlineKeyboardButton(text="Назад", callback_data="back"),
     InlineKeyboardButton(text="В меню", callback_data="menu")]]
back = InlineKeyboardMarkup(inline_keyboard=back)
go_menu=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В меню", callback_data="menu")]])
type_statik = [[InlineKeyboardButton(text='История противостояния',callback_data='history')],
    [InlineKeyboardButton(text="Команда", callback_data="team"),
     InlineKeyboardButton(text="Игрок", callback_data="player")],
    [InlineKeyboardButton(text="Назад", callback_data="back")]]
type_statik = InlineKeyboardMarkup(inline_keyboard=type_statik)
