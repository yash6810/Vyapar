# VYAPAR AI — Smart Accounting Assistant for Indian SMEs

AI-powered expense tracking, invoice management, and GST assistance via a WhatsApp-style chat interface. Built with FastAPI, React, and Google Gemini API.

## Features

- **💬 Chat-based Expense Recording** — Type or speak to record expenses in Hindi/English
- **📸 Receipt OCR** — Upload bill photos, AI extracts amount/vendor/date automatically
- **🧾 Invoice Management** — Create, track, and manage invoices with auto-numbering
- **📊 Smart Summaries** — Daily, monthly, yearly expense/invoice dashboards
- **🔐 Secure Auth** — JWT-based authentication with bcrypt password hashing
- **🗣️ Voice Input** — Browser-based speech-to-text (free, no server needed)
- **💡 GST Assistant** — Ask GST-related questions, get instant answers
- **🏷️ Categories & Tags** — Organize expenses by fuel, food, salary, etc.
- **🔍 Search & Filter** — Find expenses by vendor, category, date range

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy + Pydantic v2 |
| AI/LLM | Google Gemini API (free tier) |
| Frontend | React 18 + Custom CSS |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT + bcrypt |
| Deploy | Docker + Render.com (free) |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Gemini API Key](https://aistudio.google.com) (free)

### 1. Backend Setup

```bash
git clone https://github.com/yash6810/Vyapar.git
cd Vyapar

python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

App available at: http://localhost:3000

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/token` | Login, get JWT token |
| GET | `/api/auth/me` | Get current user profile |

### Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expenses/` | List expenses (with filters) |
| POST | `/api/expenses/` | Create expense |
| GET | `/api/expenses/summary/daily` | Today's summary |
| GET | `/api/expenses/summary/monthly` | Monthly summary |
| GET | `/api/expenses/summary/yearly` | Yearly summary |

### Invoices
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/invoices/` | List invoices |
| POST | `/api/invoices/` | Create invoice |
| POST | `/api/invoices/{id}/mark-paid` | Mark as paid |
| POST | `/api/invoices/{id}/mark-sent` | Mark as sent |

### Chat Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/webhook/text` | Process text message |
| POST | `/api/webhook/image` | Process receipt image |

## Running Tests

```bash
pytest tests/ -v
```

## Docker

```bash
docker-compose up --build
```

## Project Structure

```
Vyapar/
├── backend/
│   ├── main.py            # FastAPI app entry
│   ├── config.py          # Settings & env vars
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── crud.py            # Database operations
│   ├── auth.py            # JWT auth
│   ├── llm_service.py     # Gemini API integration
│   └── routers/
│       ├── auth.py        # Auth endpoints
│       ├── expenses.py    # Expense CRUD + summaries
│       ├── invoices.py    # Invoice CRUD + summaries
│       └── webhook.py     # Chat message processing
├── frontend/
│   └── src/
│       ├── App.js         # Routes
│       ├── api.js         # API client
│       └── components/
│           ├── Chat.js    # Main chat interface
│           ├── Dashboard.js
│           ├── Login.js
│           └── Register.js
├── tests/
│   ├── conftest.py        # Test fixtures
│   ├── test_auth.py
│   ├── test_expenses.py
│   ├── test_invoices.py
│   └── test_webhook.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## License

MIT
