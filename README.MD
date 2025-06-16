# Telegram Support Chat Bot

A simple Telegram bot for user support with a web interface to view and send messages.

---

## Description

This project implements a Telegram bot that receives messages from users and allows support agents to reply via a web interface.

- Messages are stored in a TinyDB database.
- FastAPI is used for both the API and the web interface.
- The web interface displays the list of users, message history, and allows sending replies.
- Asynchronous operations are used for Telegram API communication and database access.

---

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- httpx
- tinydb

---

## Running

1. Start the local server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Start [ngrok](https://ngrok.com) to expose your local server:

```bash
ngrok http 8000
```

3. Set the Telegram webhook, replacing `<TOKEN>` and `<NGROK_URL>`:

```bash
curl -X GET "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<NGROK_URL>/webhook"
```

4. Open the web interface:

```
http://localhost:8000/
```

---

## Usage

- The web interface lets you select a user from the list and view the message history.
- Support agents can send replies, which will be delivered to users via Telegram.
- All messages are saved in the TinyDB database `chat_db.json`.

---

## Environment Variables

- `TELEGRAM_BOT_TOKEN` — your Telegram bot token.

---

## Project Structure

```
.
├── main.py            # Main FastAPI application file
├── chat_db.json       # TinyDB database (created automatically)
├── static/            # Static files for the web interface (HTML, CSS, JS)
└── README.md          # This description
```

---

## License

MIT License
