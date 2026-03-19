import telebot
import requests
import base64
import re

# تۆکنەکەی خۆت کە ناردت
API_TOKEN = '8757664382:AAE1ZQCbH6uw4s0Bjt_lRURDnHFBlYUI_Xw'

# تێبینی: کلیلی ڤایرۆس تۆتاڵەکەت لێرە دابنێ
VT_API_KEY = '57f0783560b766b55be62be80a3ac08544fa77ba565a433d940a8b7656629e20'

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
    # تەکنیکی دۆزینەوەی لینک
    urls = re.findall(r'(https?://[^\s]+)', message.text)
    
    # گۆڕانکاری ١: ئەگەر لینک نەبوو، هیچ وەڵامێک مەدەرەوە (بۆ ئەوەی خەڵک بێزار نەبن)
    if not urls:
        return
        
    # گۆڕانکاری ٢: نیشاندانی ناوی ئەو کەسەی کە بەکاری دەهێنێت لە ناو لۆگی گیتھەب
    print(f"New Scan Request from: {message.from_user.first_name}")
        
    url_to_scan = urls[0]
    wait_msg = bot.reply_to(message, "⏳ <i>خەریکی شیکردنەوەی لینکەکە و پەیوەندیکردنم بە داتابەیسی VirusTotal...</i>")
    
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
            
            if malicious > 0 or suspicious > 0:
                status = "❌ <b>مەترسیدارە!</b> تکایە هەرگیز ئەم لینکە مەکەرەوە."
            else:
                status = "✅ <b>سەلامەتە</b> (بەپێی پشکنینی داتابەیسەکە)."
                
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
            bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=wait_msg.message_id)
            
        elif response.status_code == 404:
            bot.edit_message_text("🔍 <b>ئەم لینکە نوێیە و لە داتابەیسدا نییە!</b>\nخەریکم دەینێرم بۆ تاقیگەی ڤایرۆس تۆتاڵ بۆ پشکنینی یەکەمجار...", chat_id=message.chat.id, message_id=wait_msg.message_id)
            
            scan_api = "https://www.virustotal.com/api/v3/urls"
            payload = {"url": url_to_scan}
            requests.post(scan_api, data=payload, headers=headers)
            
            bot.send_message(message.chat.id, "✅ <b>لینکەکە بە سەرکەوتوویی ناردرا.</b>\n١ خولەکی تر دووبارە لینکەکە بنێرەوە بۆ بینینی ئەنجام.")
            
        elif response.status_code == 401:
            bot.edit_message_text("❌ <b>کێشەی API:</b> کلیلی ڤایرۆس تۆتاڵ هەڵەیە.", chat_id=message.chat.id, message_id=wait_msg.message_id)
        else:
            bot.edit_message_text(f"❌ <b>کێشەیەکی تەکنیکی ڕوویدا:</b> کۆدی {response.status_code}", chat_id=message.chat.id, message_id=wait_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("❌ <b>هەڵەیەک ڕوویدا لە پەیوەندیکردندا.</b>", chat_id=message.chat.id, message_id=wait_msg.message_id)

print("Relex Scanner Bot is successfully running...")
bot.polling()
