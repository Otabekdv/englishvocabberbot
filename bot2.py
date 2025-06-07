from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

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
# Testni boshlash komandasi
async def test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_words:
        await update.message.reply_text("Avval /daily komandasini bajarib, so'zlar oling.")
        return
    
    # Test uchun birinchi so'zni tanlaymiz
    context.user_data['test_index'] = 0
    await send_test_question(update, context)

async def send_test_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    index = context.user_data.get('test_index', 0)
    words = user_words.get(user_id, [])

    if index >= len(words):
        await update.message.reply_text("Test tugadi! Ajoyib!")
        return
    
    word = words[index]
    correct_translation = word['uz']

    # To‘g‘ri va noto‘g‘ri javoblar variantlari yaratamiz
    wrong_options = [w['uz'] for w in WORDS if w['uz'] != correct_translation]
    wrong_choices = random.sample(wrong_options, 2) if len(wrong_options) >= 2 else wrong_options

    options = wrong_choices + [correct_translation]
    random.shuffle(options)

    buttons = [
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in options
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Agar bu CallbackQuery orqali chaqirilsa, update.callback_query ni ishlatamiz, aks holda update.message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=f"Tarjimasini tanlang: {word['en']}",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=f"Tarjimasini tanlang: {word['en']}",
            reply_markup=reply_markup
        )

# Inline tugmalar bosilganda chaqiriladigan funksiya
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    index = context.user_data.get('test_index', 0)
    words = user_words.get(user_id, [])

    if index >= len(words):
        await query.answer()
        await query.edit_message_text(text="Test tugadi!")
        return

    selected_option = query.data
    correct_translation = words[index]['uz']

    if selected_option == correct_translation:
        await query.answer("To'g'ri!", show_alert=True)
        context.user_data['test_index'] = index + 1
        # Keyingi savolga o'tamiz
        await send_test_question(update, context)
    else:
        await query.answer("Noto'g'ri, qaytadan urinib ko'ring.", show_alert=True)
    

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("daily", daily))
    
    # Testni boshlash uchun handler
    app.add_handler(CommandHandler("test", test_start))
    
    # Inline tugmalar bosilganda ishlaydigan handler
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

