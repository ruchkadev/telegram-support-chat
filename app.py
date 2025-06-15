from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from tinydb import TinyDB, Query
from collections import defaultdict
import httpx
import uvicorn
from datetime import datetime

app = FastAPI()

TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"

db = TinyDB("chat_db.json")
users_table = db.table("users")
messages_table = db.table("messages")

user_chats = defaultdict(list)
last_user_chat_id = None

async def save_user(chat_id: int):
    User = Query()
    if not users_table.search(User.chat_id == chat_id):
        users_table.insert({"chat_id": chat_id})

async def save_message(chat_id: int, sender: str, text: str):
    messages_table.insert({
        "chat_id": chat_id,
        "sender": sender,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    })

async def send_reply(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
    return r.status_code, r.text

async def send_log_to_chat(text: str):
    global last_user_chat_id
    if last_user_chat_id is None:
        return
    try:
        await send_reply(last_user_chat_id, text)
    except Exception:
        pass

@app.post("/webhook")
async def telegram_webhook(update: Request):
    global last_user_chat_id
    data = await update.json()
    message = data.get("message")
    if message:
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")
        if chat_id:
            last_user_chat_id = chat_id
            user_chats[chat_id].append({"from": "user", "text": text})
            await save_user(chat_id)
            await save_message(chat_id, "user", text)
            try:
                await send_reply(chat_id, f"отправлено: {text}")
            except Exception as e:
                await send_log_to_chat(f"Ошибка при отправке ответа: {e}")
    return {"ok": True}

@app.get("/messages")
async def get_messages(chat_id: int = None):
    if chat_id is None:
        return []
    Message = Query()
    msgs = messages_table.search(Message.chat_id == chat_id)
    msgs_sorted = sorted(msgs, key=lambda x: x.get("timestamp", ""))
    return [{"from": m["sender"], "text": m["text"]} for m in msgs_sorted]

@app.get("/chat_ids")
async def get_chat_ids():
    users = users_table.all()
    return [user["chat_id"] for user in users]

@app.post("/send")
async def send_message(request: Request):
    data = await request.json()
    chat_id = data.get("chat_id")
    text = data.get("text")
    if not chat_id or not text:
        raise HTTPException(status_code=400, detail="chat_id and text required")
    user_chats[int(chat_id)].append({"from": "support", "text": text})
    await save_message(int(chat_id), "support", text)
    status_code, response_text = await send_reply(int(chat_id), text)
    if status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to send message to Telegram: {response_text}")
    return {"sent": True}

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
