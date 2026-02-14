import nest_asyncio
import asyncio
import os
import datetime
from flask import Flask
from threading import Thread
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 1. Flask Web Server (Render እንዳይዘጋው)
app = Flask('')

@app.route('/')
def home():
    return "Hana AI is Running Successfully!"

def run():
    # Render የሚሰጠውን PORT ይጠቀማል፣ ካልተሰጠ ደግሞ 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

nest_asyncio.apply()

# 2. Environment Variables (ቁልፎች)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)
user_memories = {}

# 3. Message Handler (የንግግር ክፍል)
async def handle_everything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.date.today().strftime("%B %d, %Y")

    if user_id not in user_memories:
        user_memories[user_id] = [
            {"role": "system", "content": f"Your name is Hana, a Super AI Assistant developed by Yalalem Wagaye, an IT student at UoG. Today is {today}. Respond helpfully in Amharic and English."}
        ]

    user_query = update.message.text
    if not user_query: return

    user_memories[user_id].append({"role": "user", "content": user_query})
    
    # የማስታወስ ችሎታን መገደብ (ያለፉትን 10 ንግግሮች ብቻ እንዲያስታውስ)
    if len(user_memories[user_id]) > 12:
        user_memories[user_id] = [user_memories[user_id][0]] + user_memories[user_id][-10:]

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = groq_client.chat.completions.create(
            messages=user_memories[user_id],
            model="llama-3.3-70b-versatile",
        )
        answer = response.choices[0].message.content
        user_memories[user_id].append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("ይቅርታ፣ ትንሽ ችግር አጋጥሞኛል። እባክህ ድጋሚ ሞክር!")

# 4. Main Function (ቦቱን የሚያስነሳ)
async def start_bot():
    # Flask ሰርቨሩን አስነሳ
    keep_alive()

    # የቴሌግራም ቦቱን ገንባ
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # የጽሁፍ መልእክት መቀበያ
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_everything))
    
    print("Hana is starting on Render...")
    
    # ቦቱን በ Polling መንገድ አስነሳ
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    # ቦቱ እንዳይጠፋ በ loop ውስጥ ማቆየት
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Bot stopped.")
