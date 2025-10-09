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
    {"session": "account16", "api_id": 26205265, "api_hash": "f3e66c9486fa53bed9935ce4b2b1d0bf", "message": " 1401126135"},
    {"session": "account17", "api_id": 27806803, "api_hash": "730d48697849a6d0f63052120b2cf3b4", "message": " 1401140311"},
    {"session": "account18", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1401144185"},
    {"session": "account19", "api_id": 13195192, "api_hash": "ca944410b25fb1e852d8c9f934759e9d", "message": " 1401148101"},
    {"session": "account20", "api_id": 27187404, "api_hash": "b5e0ce0579333c3c0ef85f7d6e6d1cfd", "message": " 1401156291"},
    {"session": "account21", "api_id": 20262983, "api_hash": "d233b0bf40f861ce947ec5e95510300e", "message": " 1401163777"},
    {"session": "account22", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376794163"},
    {"session": "account23", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376795309"},
    {"session": "account24", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376796431"},
    {"session": "account25", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376797385"},
    {"session": "account26", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376799585"},
    {"session": "account27", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376800587"},
    {"session": "account28", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376801427"},
    {"session": "account29", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376802667"},
    {"session": "account30", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": " 1376803621"},
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













