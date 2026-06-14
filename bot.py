import telebot
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
    
    # PDF banao command
    if "pdf banao" in text.lower():
        pending = user_data[uid]["pending"]
        
        # Debug: Kitne prompts ne?
        print(f"User {uid} has {len(pending)} prompts")
        
        if not pending:
            bot.reply_to(m, "❌ Koi prompt nahi hai! Pehle kuch likho.")
            return
        
        # PDF file name
        filename = f"prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # PDF banao
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom style for better visibility
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=12,
            leading=14
        )
        
        story = []
        
        # Title
        story.append(Paragraph("MY SAVED PROMPTS", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Total Prompts: {len(pending)}", normal_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 30))
        
        # Saare prompts likho
        for i, p in enumerate(pending, 1):
            # Get prompt text
            if isinstance(p, dict):
                txt = p.get('text', str(p))
            else:
                txt = str(p)
            
            # Add to PDF
            story.append(Paragraph(f"<b>Prompt #{i}</b>", styles['Heading2']))
            story.append(Spacer(1, 5))
            story.append(Paragraph(txt.replace('\n', '<br/>'), normal_style))
            story.append(Spacer(1, 15))
        
        # PDF build karo
        try:
            doc.build(story)
            print(f"PDF created: {filename}")
        except Exception as e:
            print(f"PDF build error: {e}")
            bot.reply_to(m, f"❌ PDF error: {str(e)}")
            return
        
        # PDF bhejo
        with open(filename, 'rb') as f:
            bot.send_document(uid, f, caption=f"✅ PDF ban gayi! {len(pending)} prompts")
        
        # Clean up
        os.remove(filename)
        
        # Clear pending prompts
        user_data[uid]["pending"] = []
        save(user_data)
        bot.send_message(uid, f"📊 {len(pending)} prompts di PDF ban gayi! Nave prompts lai fer likho.")
    
    else:
        # Prompt save karo
        prompt_data = {
            "text": text,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        user_data[uid]["pending"].append(prompt_data)
        save(user_data)
        
        count = len(user_data[uid]["pending"])
        
        # Confirmation with preview
        preview = text[:50] + "..." if len(text) > 50 else text
        bot.reply_to(
            m, 
            f"✅ Prompt #{count} save!\n\n📝 '{preview}'\n\n💡 '{count}' prompts ne. 'pdf banao' likhoge ta PDF banegi."
        )
        
        # Debug print
        print(f"Saved prompt for {uid}: {text[:50]}")

print("🤖 Bot started! Waiting for messages...")
bot.infinity_polling()
