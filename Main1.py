import telebot
import requests
import base64
import re
from telebot import types

# زانیارییەکانت
API_TOKEN = '8757664382:AAE1ZQCbH6uw4s0Bjt_lRURDnHFBlYUI_Xw'
VT_API_KEY = '57f0783560b766b55be62be80a3ac08544fa77ba565a433d940a8b7656629e20'

bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')

# ١. بەشی فەرمانی ستارت و دروستکردنی دوگمەکان
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👤 گەشەپێدەر")
    btn2 = types.KeyboardButton("📥 داگرتنی G-VORTEX")
    btn3 = types.KeyboardButton("❓ ڕێنمایی")
    markup.add(btn1, btn2, btn3)
    
    text = (
        f"🛡️ <b>سڵاو {message.from_user.first_name}! بەخێرهاتی بۆ Relex Scanner.</b>\n\n"
        "من ئامادەم بۆ پشکنینی هەر لینکێکی گوماناوی و پاراستنی تۆ.\n"
        "تەنها لینکەکە بنێرە یان دوگمەکانی خوارەوە بەکاربهێنە."
    )
    bot.reply_to(message, text, reply_markup=markup)

# ٢. وەڵامدانەوەی دوگمەی گەشەپێدەر
@bot.message_handler(func=lambda message: message.text == "👤 گەشەپێدەر")
def dev_info(message):
    bot.reply_to(message, "👨‍💻 <b>گەشەپێدەر:</b> @Relexm\n🚀 شارەزا لە بواری سایبەر سیکیوێریتی و پەرەپێدانی سۆفتوێر.")

# ٣. وەڵامدانەوەی دوگمەی ڕێنمایی
@bot.message_handler(func=lambda message: message.text == "❓ ڕێنمایی")
def help_info(message):
    bot.reply_to(message, "💡 <b>چۆن بەکارم دەهێنیت؟</b>\n\nتەنها هەر لینکێکت لایە (http یان https) لێرە Pasteی بکە، من یەکسەر پێت دەڵێم مەترسیدارە یان نا.")

# ٤. ناردنی لینکی بەرنامەی G-VORTEX لە چەناڵەکەتەوە
@bot.message_handler(func=lambda message: message.text == "📥 داگرتنی G-VORTEX")
def send_apk(message):
    # دروستکردنی دوگمەیەکی شین (Inline) لە ژێر نامەکەدا
    markup = types.InlineKeyboardMarkup()
    channel_post_url = "https://t.me/ayax1mm/56"
    btn_link = types.InlineKeyboardButton("🚀 کلیک بکە بۆ داگرتن لە چەناڵ", url=channel_post_url)
    markup.add(btn_link)
    
    text = (
        "📦 <b>بەرنامەی G-VORTEX Premium</b>\n\n"
        "بۆ داگرتنی بەرنامەکە بە شێوەیەکی سەلامەت و خێرا، کلیک لە دوگمەی خوارەوە بکە و لە چەناڵەکەمان دایبەزێنە.\n\n"
        "🛡️ <i>ئەم فایلە پێشتر لەلایەن Relex Scanner پشکنراوە.</i>"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ٥. لۆژیکی سەرەکی سکانکردنی لینکەکان
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    urls = re.findall(r'(https?://[^\s]+)', message.text)
    
    if not urls:
        return # بێدەنگ دەبێت ئەگەر نامەکە لینک یان دوگمە نەبوو
        
    print(f"New Scan Request from: {message.from_user.first_name}")
        
    url_to_scan = urls[0]
    wait_msg = bot.reply_to(message, "⏳ <i>خەریکی شیکردنەوەی لینکەکە و پەیوەندیکردنم بە داتابەیس...</i>")
    
    url_id = base64.urlsafe_b64encode(url_to_scan.encode()).decode().strip("=")
    api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = {"accept": "application/json", "x-apikey": VT_API_KEY}
    
    try:
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            
            malicious = stats['malicious']
            suspicious = stats['suspicious']
            
            status = "❌ <b>مەترسیدارە!</b>" if (malicious > 0 or suspicious > 0) else "✅ <b>سەلامەتە.</b>"
                
            result_text = (
                f"🛡️ <b>ئەنجامی پشکنینی Relex Scanner</b>\n\n"
                f"🔗 <b>لینک:</b> {url_to_scan}\n\n"
                f"🔴 مەترسیدار: <b>{malicious}</b>\n"
                f"🟠 گوماناوی: <b>{suspicious}</b>\n"
                f"🟢 سەلامەت: <b>{stats['harmless']}</b>\n\n"
                f"💡 <b>بڕیار:</b> {status}\n\n"
                f"👨‍💻 گەشەپێدەر: @Relexm"
            )
            bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=wait_msg.message_id)
            
        elif response.status_code == 404:
            bot.edit_message_text("🔍 <b>ئەم لینکە نوێیە!</b>\nناردرا بۆ پشکنینی یەکەمجار. خولەکێکی تر دووبارە لینکەکە بنێرەوە بۆ بینینی ئەنجام.", chat_id=message.chat.id, message_id=wait_msg.message_id)
            requests.post("https://www.virustotal.com/api/v3/urls", data={"url": url_to_scan}, headers=headers)
        else:
            bot.edit_message_text("❌ کێشەیەکی تەکنیکی لە سێرڤەر ڕوویدا.", chat_id=message.chat.id, message_id=wait_msg.message_id)
            
    except Exception:
        bot.edit_message_text("❌ هەڵەیەک ڕوویدا لە پەیوەندیکردندا.", chat_id=message.chat.id, message_id=wait_msg.message_id)

print("Relex Scanner Bot is successfully running...")
bot.polling()
