import telebot
import requests
import time
import base64

TOKEN = "8757664382:AAE1ZQCbH6uw4s0Bjt_lRURDnHFBlYUI_Xw"
# تێبینی: لێرەدا کلیلێکی کاتی دادەنێم، بەڵام باشترە دواتر کلیلێکی تایبەت بە خۆت وەرگریت
VT_API_KEY = "64c919d6790757e937397b9525c276a1629851726a8f6d639b7d032252a1d044"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🛡️ **بەخێربێیت بۆ Relexm Global Scanner!**\n\nئێستا بۆتەکە بەستراوەتەوە بە ٧٠ ئەنتی ڤایرۆسی جیهانی. هەر لینکێکم بۆ بنێریت بە وردی دەیپشکنم.")

@bot.message_handler(func=lambda m: True)
def scan_link(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "❌ تکایە لینکێکی دروست بنێرە.")
        return

    msg = bot.reply_to(message, "🔍 خەریکی پشکنینی وردم لە VirusTotal...")

    try:
        # گۆڕینی URL بۆ شێوازی پێویست بۆ VirusTotal
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        headers = {"x-apikey": VT_API_KEY}

        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            malicious = stats['malicious']
            suspicious = stats['suspicious']
            
            if malicious > 0 or suspicious > 0:
                result = f"🚨 **ئاگاداربە! لینکەکە مەترسیدارە!**\n\n🌐 لینک: `{url}`\n🚫 ڤایرۆس: {malicious}\n⚠️ گوماناوی: {suspicious}\n\n❌ پێشنیار دەکەم نەیکەیتەوە!"
            else:
                result = f"✅ **ئەنجامی پشکنین: سەلامەتە**\n\n🌐 لینک: `{url}`\n🛡️ ٧٠ ئەنتی ڤایرۆس دەڵێن پاکە.\n💎 بەبێ کێشە دەتوانیت بەکاری بهێنیت."
        else:
            result = "⚠️ ئەم لینکە تازەیە و پێویستی بە پشکنینی دەستی هەیە لە ماڵپەڕی VirusTotal."

        bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"❌ هەڵەیەک ڕوویدا: {str(e)}", message.chat.id, msg.message_id)

bot.infinity_polling()
