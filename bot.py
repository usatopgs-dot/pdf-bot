import telebot
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import black  # BLACK color add kitta

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
    
    if text.lower() == "pdf banao":
        pending = user_data[uid].get("pending", [])
        
        if not pending:
            bot.reply_to(m, "❌ Koi prompt nahi hai! Pehle kuch likho.")
            return
        
        filename = f"prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Title style - Black color
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=black  # Black color
        )
        
        # Normal text style - Black color
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=black,  # Black color
            leading=14
        )
        
        # Heading style - Black color
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=13,
            alignment=TA_LEFT,
            spaceAfter=5,
            textColor=black,  # Black color
            leading=15
        )
        
        story = []
        story.append(Paragraph("MY SAVED PROMPTS", title_style))
        story.append(Paragraph(f"Total Prompts: {len(pending)}", normal_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 30))
        
        for i, p in enumerate(pending, 1):
            prompt_text = str(p)
            story.append(Paragraph(f"Prompt #{i}", heading_style))
            story.append(Spacer(1, 5))
            story.append(Paragraph(prompt_text, normal_style))
            story.append(Spacer(1, 15))
        
        doc.build(story)
        
        with open(filename, 'rb') as f:
            bot.send_document(uid, f, caption=f"✅ PDF ban gayi! {len(pending)} prompts")
        
        os.remove(filename)
        user_data[uid]["pending"] = []
        save(user_data)
        bot.send_message(uid, f"✅ PDF ban gayi! Ab nave prompts likho.")
    
    else:
        # Save prompt
        user_data[uid]["pending"].append(text)
        save(user_data)
        count = len(user_data[uid]["pending"])
        bot.reply_to(m, f"✅ Prompt #{count} save!\n\n'{text[:100]}'\n\n'{count}' prompts ne. 'pdf banao' likhoge ta PDF banegi.")

print("🤖 Bot started! Send any message to save, then type 'pdf banao'")
bot.infinity_polling()
