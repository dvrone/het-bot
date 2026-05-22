<div align="center">

# 🤖 het-bot

### Official Telegram bot for JSC "Karakalpak Regional Electric Networks Enterprise"

<br>

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.26-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://docs.aiogram.dev)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat)](https://sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-1.18-blue?style=flat)](https://alembic.sqlalchemy.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

<br>

[Features](#features) · [Quick Start](#quick-start) · [Project Structure](#project-structure) · [Configuration](#configuration) · [Author](#author)

</div>

---

## Overview

**het-bot** is an async Telegram bot for [JSC "Karakalpak Regional Electric Networks Enterprise"](https://www.het.uz/en/lists/view/73) — a subsidiary of JSC "Regional Electric Networks" of Uzbekistan. The bot handles citizen registration and service requests. Users register with their personal details, submit requests by category, and receive replies directly through Telegram in their preferred language.

---

## Features

- 🌐 **Multilingual** — Qaraqalpaq (Karakalpak), Uzbek, and Russian
- 📝 **Step-by-step registration** — full name, contact type, phone, region, district, address, account number
- 🏢 **Individual & Legal** — separate flows with account number validation (7 digits for individual, 6 for legal)
- 📨 **Request categories** — Power Outage and General Inquiry with separate admin routing
- 🛡 **Admin panel** — registered users, request list with filter (pending/replied) and pagination
- 👤 **Profile** — view and edit all fields inline
- 🔀 **Smart admin routing** — outage requests → `OUTAGE_ADMIN_IDS`, others → `GENERAL_ADMIN_IDS`
- ⚡ **Fully async** — aiogram 3 + async SQLAlchemy + aiosqlite
- 🗄 **Alembic migrations** — safe database schema changes
- 🐳 **Docker ready** — one command deploy

---

## Quick Start

### 1. Clone & install

```bash
git clone git@github.com:dvrone/het-bot.git
cd het-bot
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=sqlite:///het.db
ADMIN_IDS=123456789
OUTAGE_ADMIN_IDS=123456789
GENERAL_ADMIN_IDS=987654321
```

### 3. Run migrations & start

```bash
alembic upgrade head
python main.py
```

### 4. Or run with Docker

```bash
docker build -t het-bot .
docker run --env-file .env het-bot
```

---

## Project Structure

```
het-bot/
├── main.py                   # Entry point
├── core/
│   ├── config.py             # ENV vars, logging, admin IDs
│   ├── database.py           # Async SQLAlchemy engine & session
│   └── texts.py              # i18n helper t(), JSON loaders
├── bot/
│   ├── fsm/
│   │   └── states.py         # FSM state groups
│   ├── handlers/
│   │   ├── start.py          # /start, language selection
│   │   ├── register.py       # Registration flow
│   │   ├── request.py        # /request — submit a request
│   │   ├── profile.py        # /profile — view & edit profile
│   │   ├── admin.py          # /admin, /users, /requests, reply
│   │   └── fallback.py       # /help, /cancel, unknown messages
│   ├── keyboards/
│   │   ├── inline.py         # All inline keyboards
│   │   └── reply.py          # Phone share keyboard
│   ├── models/
│   │   └── user.py           # User & Request SQLAlchemy models
│   ├── services/
│   │   ├── db.py             # Async DB helpers
│   │   └── notify.py         # Admin notifications, smart routing
│   └── utils/
│       ├── phone.py          # Uzbek phone number normalizer
│       └── validators.py     # Account number validator
├── migrations/               # Alembic migration files
├── texts.json                # UI strings in kaa / uz / ru
├── districts.json            # Districts of Karakalpakstan
├── request_types.json        # Request categories and types
├── Dockerfile
└── requirements.txt
```

---

## Configuration

| Variable | Description | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/BotFather) | required |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///het.db` |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | `""` |
| `OUTAGE_ADMIN_IDS` | Admins for power outage requests | `""` |
| `GENERAL_ADMIN_IDS` | Admins for general requests | `""` |

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Begin registration |
| `/profile` | View and edit profile |
| `/request` | Submit a service request |
| `/help` | Show available commands |
| `/cancel` | Cancel current action |
| `/admin` | Admin stats (admins only) |
| `/users` | List registered users (admins only) |
| `/requests` | View requests with filter (admins only) |

---

## Tech Stack

| Library | Purpose |
|---|---|
| [aiogram 3](https://docs.aiogram.dev) | Async Telegram bot framework |
| [SQLAlchemy 2](https://sqlalchemy.org) | Async ORM |
| [Alembic](https://alembic.sqlalchemy.org) | Database migrations |
| [aiosqlite](https://github.com/omnilib/aiosqlite) | Async SQLite driver |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variables |

---

## License

MIT