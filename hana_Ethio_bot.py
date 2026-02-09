import nest_asyncio
import asyncio
import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import datetime

nest_asyncio.apply()

# Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)
user_memories = {}

async def handle_everything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.date.today().strftime("%B %d, %Y")

    if user_id not in user_memories:
        user_memories[user_id] = [
            {"role": "system", "content": f"Your name is Hana, a Super AI Assistant developed by Yalalem wagaye uog IT STUDENT. Today is {today}."}
        ]

    user_query = update.message.text
    if not user_query: return

    user_memories[user_id].append({"role": "user", "content": user_query})
    
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
        await update.message.reply_text("I'm having a little trouble. Let's try again!")

async def main():
    # Render "Port" ቼክ ስለሚያደርግ የውሸት ሰርቨር ማስነሳት
    import http.server
    import socketserver
    import threading
    
    def run_dummy():
        PORT = int(os.environ.get("PORT", 8080))
        with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    
    threading.Thread(target=run_dummy, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_everything))
    
    print("Hana is starting on Render...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
