import re
import pytesseract
from PIL import Image
from telethon import TelegramClient, events, errors
from sympy import sympify
from sympy.core.sympify import SympifyError
import asyncio
import os
from flask import Flask
import threading
import requests

# Kanal username
channel_username = 'kurator_kazino'

accounts = [
    {"session": "account7", "api_id": 22549665, "api_hash": "af7f7a7782c4d529b51564528f5bddbc", "message": "1362398355"},
    {"session": "account8", "api_id": 26205265, "api_hash": "f3e66c9486fa53bed9935ce4b2b1d0bf", "message": "1362398693"},
    {"session": "account9", "api_id": 29183260, "api_hash": "3e5ece984e7df9cc5780f3f5731fabcf", "message": "1362399019"},
]


clients = []

# Matematika ifodani ajratish
def extract_expression(text):
    text = re.sub(r'(?<=\d)\s*[xX]\s*(?=\d)', '*', text)
    pattern = r'[\d\s\+\-\*/\^\(\)]+'
    matches = re.findall(pattern, text)
    if matches:
        for m in matches:
            clean = m.strip()
            if clean.isdigit():
                continue
            if any(op in clean for op in ['+', '-', '*', '/', '^']):
                return clean
    return None

# Yangi xabar kelganda ishlaydigan funksiya
async def handle_event(client):
    @client.on(events.NewMessage(chats=channel_username))
    async def handler(event):
        raw_text = event.raw_text
        if raw_text.strip():
            expr = extract_expression(raw_text)
        else:
            file_path = await event.download_media()
            if file_path:
                try:
                    img = Image.open(file_path)
                    raw_text = pytesseract.image_to_string(img)
                    expr = extract_expression(raw_text)
                finally:
                    os.remove(file_path)
            else:
                expr = None

        if not expr:
            print(f"[{client.session.filename}] ℹ️ Matematik ifoda topilmadi.")
            return

        try:
            result = sympify(expr)
            await client.send_message(
                entity=channel_username,
                message=f"{result}",
                comment_to=event.id
            )
            print(f"[{client.session.filename}] ✅ Izoh yuborildi: {expr} = {result}")
        except SympifyError:
            print(f"[{client.session.filename}] ❌ Noto‘g‘ri ifoda: {expr}")
        except Exception as e:
            print(f"[{client.session.filename}] ⚠️ Xatolik: {e}")

# Akkauntni ishga tushirish
async def start_client(acc):
    client = TelegramClient(acc['session'], acc['api_id'], acc['api_hash'])
    await client.start()
    await handle_event(client)
    print(f"🔗 {acc['session']} ulandi.")
    return client

async def telegram_main():
    global clients
    clients = await asyncio.gather(*(start_client(acc) for acc in accounts))
    print("🤖 Hammasi ishga tushdi. Kanal kuzatilyapti...")
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

# Flask server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti!"

# Har 5 daqiqada o‘zini ping qilish
def ping_self():
    url = os.environ.get("RENDER_URL", "https://kuratorjon.onrender.com")
    while True:
        try:
            requests.get(url)
            print("✅ Ping yuborildi")
        except Exception as e:
            print(f"❌ Ping xatosi: {e}")
        asyncio.run(asyncio.sleep(300))

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=ping_self).start()
    asyncio.run(telegram_main())







