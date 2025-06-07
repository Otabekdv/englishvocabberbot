from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random

TOKEN = '8192745695:AAEVMIXpIoMTam_CAD1jstejoq2PEuwWu2Y'  # <-- bu yerga o'z tokeningizni yozing!

# Fayldan so'zlarni o'qish funksiyasi
def load_words(filename):
    words = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ' - ' in line:
                en, uz = line.split(' - ', 1)
                words.append({"en": en.strip(), "uz": uz.strip()})
    return words

# Fayl to'liq manzili (ish stolida)
WORDS = load_words(r'C:\Users\user\Desktop\yuqori_darajadagi_ingliz_sozlar.txt')

user_words = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Har kuni 10 ta yangi so'z yuboraman. /daily ni bosing.")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(WORDS) < 10:
        await update.message.reply_text("Faylda 10 tadan kam so'z bor.")
        return
    words = random.sample(WORDS, 10)
    user_words[user_id] = words
    msg = "\n".join([f"{w['en']} - {w['uz']}" for w in words])
    await update.message.reply_text(f"Bugungi so'zlaringiz:\n{msg}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("daily", daily))
    app.run_polling()
