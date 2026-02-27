from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def join_channel_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga o‘tish", url="https://t.me/YOUR_CHANNEL")],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
    ])

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Test yaratish", callback_data="create_test")],
        [InlineKeyboardButton("▶️ Test ishlash", callback_data="take_test")],
        [InlineKeyboardButton("🏆 TOP 10", callback_data="top")],
        [InlineKeyboardButton("👑 Eng faol yaratuvchilar", callback_data="top_creators")]
    ])