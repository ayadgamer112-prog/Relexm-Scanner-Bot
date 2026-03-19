import telebot
import requests
import base64
import re

# تۆکنەکەی خۆت کە ناردت
API_TOKEN = '8757664382:AAE1ZQCbH6uw4s0Bjt_lRURDnHFBlYUI_Xw'

# تێبینی: کلیلی ڤایرۆس تۆتاڵەکەت لێرە دابنێ لە نێوان جووتە کۆتەیشنەکان
VT_API_KEY = '57f0783560b766b55be62be80a3ac08544fa77ba565a433d940a8b7656629e20'

# بەکارهێنانی parse_mode='HTML' بۆ دیزاینێکی جوانتر
bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "🛡️ <b>سڵاو! من Relex Scanner-م.</b>\n\n"
        "ئامادەم بۆ پشکنینی هەر لینکێک (http یان https) بۆ دڵنیابوون لە سەلامەتی.\n"
        "تەنها لینکەکەم بۆ بنێرە."
    )
    bot.reply_to(message, text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # تەکنیکی پێشکەوتوو: دۆزینەوەی لینک لە ناو دەقدا بە Regex
    urls = re.findall(r'(https?://[^\s]+)', message.text)
    
    if not urls:
        bot.reply_to(message, "⚠️ <b>هەڵە:</b> هیچ لینکێکی ڕاست و دروست نەدۆزرایەوە لە نامەکەتدا.")
        return
        
    url_to_scan = urls[0]
    
    # ناردنی نامەی چاوەڕوانی
    wait_msg = bot.reply_to(message, "⏳ <i>خەریکی شیکردنەوەی لینکەکە و پەیوەندیکردنم بە داتابەیسی VirusTotal...</i>")
    
    # ئامادەکردنی لینکەکە بۆ ڤایرۆس تۆتاڵ (ئینکۆدکردنی بە Base64)
    url_id = base64.urlsafe_b64encode(url_to_scan.encode()).decode().strip("=")
    api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            
            malicious = stats['malicious']
            suspicious = stats['suspicious']
            harmless = stats['harmless']
            undetected = stats['undetected']
            
            # دروستکردنی لۆژیکی بڕیاردان
            if malicious > 0 or suspicious > 0:
                status = "❌ <b>مەترسیدارە!</b> تکایە هەرگیز ئەم لینکە مەکەرەوە."
            else:
                status = "✅ <b>سەلامەتە</b> (بەپێی پشکنینی داتابەیسەکە)."
                
            # دیزاینکردنی ئەنجامەکە بە شێوەیەکی پرۆفیشناڵ
            result_text = f"""
🛡️ <b>ئەنجامی پشکنینی Relex Scanner</b> 🛡️

🔗 <b>لینک:</b> {url_to_scan}

📊 <b>ئاماری پشکنین:</b>
🔴 مەترسیدار: <b>{malicious}</b> ئەنتی‌ڤایرۆس
🟠 گوماناوی: <b>{suspicious}</b> ئەنتی‌ڤایرۆس
🟢 سەلامەت: <b>{harmless}</b> ئەنتی‌ڤایرۆس
⚪ نەناسراو: {undetected}

💡 <b>بڕیاری کۆتایی:</b>
{status}
"""
            # گۆڕینی نامە چاوەڕوانییەکە بۆ ئەنجامەکە (بۆ ئەوەی پڕۆفیشناڵتر دەربکەوێت)
            bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=wait_msg.message_id)
            
        elif response.status_code == 404:
            bot.edit_message_text("⚠️ <b>تێبینی:</b> ئەم لینکە تا ئێستا لە ڤایرۆس تۆتاڵ پشکنینی بۆ نەکراوە، یان پێویستی بە پشکنینی نوێیە.", chat_id=message.chat.id, message_id=wait_msg.message_id)
        elif response.status_code == 401:
            bot.edit_message_text("❌ <b>کێشەی API:</b> کلیلی ڤایرۆس تۆتاڵ هەڵەیە یان دانەنراوە.", chat_id=message.chat.id, message_id=wait_msg.message_id)
        else:
            bot.edit_message_text(f"❌ <b>کێشەیەکی تەکنیکی ڕوویدا:</b> کۆدی {response.status_code}", chat_id=message.chat.id, message_id=wait_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("❌ <b>هەڵەیەک ڕوویدا لە پەیوەندیکردندا بە سێرڤەر.</b>", chat_id=message.chat.id, message_id=wait_msg.message_id)

print("Relex Scanner Bot is successfully running...")
bot.polling()
