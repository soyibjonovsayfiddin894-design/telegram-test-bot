from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Part 1", callback_data="part1")],
        [InlineKeyboardButton("Part 2", callback_data="part2")]
    ]
    return InlineKeyboardMarkup(keyboard)

def yes_no_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ha", callback_data="yes")],
        [InlineKeyboardButton("Yoq", callback_data="no")]
    ]
    return InlineKeyboardMarkup(keyboard)
