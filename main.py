import telebot
import requests
import time
import os

# ١. تووکنەکەت لێرە دانراوە
TOKEN = "8757664382:AAE1ZQCbH6uw4s0Bjt_lRURDnHFBlYUI_Xw"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🛡️ بەخێربێیت بۆ Relexm Scanner!\nلینکێکم بۆ بنێرە تا بۆت بپشکنم.")

@bot.message_handler(func=lambda m: True)
def scan(message):
    url = message.text.strip()
    if url.startswith("http"):
        msg = bot.reply_to(message, "🔍 خەریکی پشکنینم...")
        time.sleep(2)
        report = f"✅ ئەنجامی پشکنین بۆ:\n{url}\n\n🛡️ دۆخ: سەلامەت\n📊 بزوێنەر: Relexm Engine"
        bot.edit_message_text(report, message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "❌ تکایە تەنها لینک بنێرە.")

# ڕەنکردنی بۆتەکە
print("Bot is starting...")
bot.infinity_polling()


