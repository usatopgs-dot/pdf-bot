import telebot
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

user_data = load()

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = str(m.chat.id)
    text = m.text.strip()
    
    if uid not in user_data:
        user_data[uid] = {"pending": []}
        save(user_data)
    
    if "pdf banao" in text.lower():
        pending = user_data[uid]["pending"]
        if not pending:
            bot.reply_to(m, "❌ Koi prompt nahi hai! Pehle kuch likho.")
            return
        
        # PDF banao
        filename = f"prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"MY PROMPTS", styles['Title']))
        story.append(Paragraph(f"Total: {len(pending)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        for i, p in enumerate(pending, 1):
            if isinstance(p, dict):
                txt = p.get('text', str(p))
            else:
                txt = str(p)
            story.append(Paragraph(f"{i}. {txt}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        doc.build(story)
        
        with open(filename, 'rb') as f:
            bot.send_document(uid, f)
        os.remove(filename)
        
        user_data[uid]["pending"] = []
        save(user_data)
        bot.send_message(uid, f"✅ PDF ban gayi! {len(pending)} prompts.")
    
    else:
        user_data[uid]["pending"].append({"text": text, "date": str(datetime.now())})
        save(user_data)
        count = len(user_data[uid]["pending"])
        bot.reply_to(m, f"✅ Prompt #{count} save! 'pdf banao' likhoge ta PDF banegi.")

print("🤖 Bot started...")
bot.infinity_polling()
