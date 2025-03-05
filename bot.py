import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from database import Book, session
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

# --- أوامر البوت ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! اكتب اسم الكتاب أو المؤلف للبحث.")

def handle_channel_post(update: Update, context: CallbackContext):
    """يتتبع الكتب الجديدة في القناة ويخزنها في قاعدة البيانات."""
    if update.channel_post:
        msg = update.channel_post
        # مثال: النص يجب أن يكون "العنوان: كتاب الفلسفة | المؤلف: علي حسن"
        text = msg.text or msg.caption
        if text and "|" in text:
            title_part, author_part = text.split("|", 1)
            title = title_part.replace("العنوان:", "").strip()
            author = author_part.replace("المؤلف:", "").strip()
            # حفظ البيانات
            new_book = Book(title=title, author=author, message_id=msg.message_id)
            session.add(new_book)
            session.commit()

def search_book(update: Update, context: CallbackContext):
    """يبحث عن الكتاب في قاعدة البيانات ويرسل الرابط."""
    query = update.message.text
    books = session.query(Book).filter(
        (Book.title.ilike(f"%{query}%")) | 
        (Book.author.ilike(f"%{query}%"))
    ).all()
    
    if not books:
        update.message.reply_text("⚠️ الكتاب غير متوفر حالياً.")
        return
    
    for book in books:
        message_link = f"https://t.me/{CHANNEL_USERNAME}/{book.message_id}"
        update.message.reply_text(f"📚 {book.title}:\n{message_link}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # تعريف الأوامر
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_book))
    dp.add_handler(MessageHandler(Filters.update.channel_post, handle_channel_post))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
