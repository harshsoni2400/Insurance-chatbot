# NYVO Insurance Advisor Chatbot

AI-powered Insurance Advisor Chatbot for NYVO that helps customers in India understand and purchase insurance products.

## Features

- 💬 **Natural Language Chat**: Conversational AI to answer insurance questions
- 🎯 **Smart Recommendations**: Personalized policy suggestions based on user needs
- 📚 **Knowledge Base (RAG)**: Educational content about insurance in India
- 🔍 **Policy Comparison**: Compare multiple policies side by side
- 🏥 **Health Insurance**: Coverage guidance for individual, family, senior citizen plans
- 💰 **Term Insurance**: Help with term life insurance selection and coverage calculation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Chat API    │  │ Recommend   │  │ Content Management  │  │
│  │             │  │ Engine      │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         ▼                ▼                     ▼             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Chatbot Service (OpenAI GPT-4)             ││
│  └─────────────────────────┬───────────────────────────────┘│
└─────────────────────────────┼───────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  ChromaDB       │  │  SQLite/        │  │  OpenAI API     │
│  (Vector Store) │  │  PostgreSQL     │  │  (Embeddings +  │
│                 │  │  (Policies DB)  │  │   Completions)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- OpenAI API key

### 2. Installation

```bash
# Clone/navigate to project
cd nyvo-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 4. Initialize Database & Content

```bash
# Initialize database with sample data
python scripts/seed_data.py

# Start the server (this also indexes content)
python -m app.main
```

### 5. Index Content Library

After starting the server, index your content:

```bash
curl -X POST http://localhost:8000/api/v1/content/ingest
```

### 6. Launch Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
# Using Python's built-in server
cd frontend && python -m http.server 3000
```

Then visit: http://localhost:3000

## API Endpoints

### Chat

```bash
# Main chat endpoint
POST /api/v1/chat
{
    "message": "What is term insurance?",
    "session_id": "user123",
    "conversation_history": []
}

# Streaming chat
POST /api/v1/chat/stream
```

### Recommendations

```bash
# Health insurance recommendations
POST /api/v1/recommend/health
{
    "age": 30,
    "coverage_needed": 1000000,
    "budget_monthly": 1500,
    "family_size": 3
}

# Term insurance recommendations
POST /api/v1/recommend/term
{
    "age": 30,
    "coverage_needed": 10000000,
    "annual_income": 1200000,
    "smoker": false
}
```

### Policy Details

```bash
# Get policy details
GET /api/v1/policy/{policy_id}

# Compare policies
POST /api/v1/policy/compare
{
    "policy_ids": [1, 2, 3]
}
```

### Content Management

```bash
# Ingest content library
POST /api/v1/content/ingest

# Get content stats
GET /api/v1/content/stats
```

## Content Library

Add your content files to `nyvo-content/` directory:

```
nyvo-content/
├── health-insurance-basics.md
├── term-insurance-guide.md
├── insurance-claim-process.md
├── faq-insurance-basics.md
├── regulations/
│   └── irdai-guidelines.md
└── policies/
    └── product-details.md
```

Supported formats: `.md`, `.txt`, `.pdf`, `.docx`

After adding content, run the ingestion endpoint to index it.

## Database Schema

### Insurance Providers
- Company details
- Claim settlement ratio
- IRDAI registration

### Insurance Policies
- Policy details (name, type, description)
- Coverage (min/max, details)
- Eligibility (age, income)
- Premium information
- Features, riders, exclusions
- Ratings

### User Profiles
- Demographics
- Financial details
- Preferences

### Chat Sessions
- Conversation history
- Context used
- Recommendations made

## Deployment

### Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python scripts/seed_data.py

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t nyvo-chatbot .
docker run -p 8000:8000 --env-file .env nyvo-chatbot
```

### Production Considerations

1. **Database**: Use PostgreSQL for production
2. **Vector Store**: Consider Pinecone/Weaviate for scale
3. **Caching**: Add Redis for conversation caching
4. **Rate Limiting**: Implement rate limiting on API
5. **Authentication**: Add JWT auth for secure access
6. **Monitoring**: Add logging and metrics (Prometheus/Grafana)

## Customization

### Adding New Insurance Types

1. Add enum value in `models/database.py`:
```python
class InsuranceType(enum.Enum):
    MOTOR = "motor"  # Add new type
```

2. Add recommendation method in `services/recommendation_engine.py`

3. Add endpoint in `api/routes.py`

### Modifying the System Prompt

Edit the `SYSTEM_PROMPT` in `services/chatbot.py` to customize the AI's personality, guidelines, and knowledge boundaries.

### Adding Content

1. Add `.md` or other supported files to `nyvo-content/`
2. Call `POST /api/v1/content/ingest` to re-index

## Support

For issues or questions:
- Check the API docs at `/docs` (Swagger UI)
- Review logs for error details
- Ensure OpenAI API key is valid and has credits

## License

Proprietary - NYVO Internal Use Only

******

! I've built a complete NYVO Insurance Advisor Chatbot system. Here's what's included:

📁 Project Structure
nyvo-chatbot/
├── app/
│   ├── api/          # FastAPI routes & schemas
│   ├── core/         # Configuration
│   ├── models/       # Database models (policies, providers, users)
│   ├── services/     # Core logic
│   │   ├── chatbot.py              # OpenAI-powered conversation
│   │   ├── vector_store.py         # RAG with ChromaDB
│   │   └── recommendation_engine.py # Policy matching
│   └── main.py       # FastAPI app entry
├── frontend/         # Chat interface (HTML/JS)
├── nyvo-content/     # Knowledge base (4 comprehensive guides)
├── scripts/          # Database seeding
├── requirements.txt
├── run.sh           # One-click startup
└── README.md
✨ Features Built
Feature	Description
RAG System	Content library indexed in ChromaDB for accurate answers
Smart Recommendations	Scores policies based on age, income, coverage needs, CSR
Intent Detection	Recognizes health/term queries, recommendation requests
Streaming Chat	Real-time response streaming
Sample Data	8 insurers + 9 policies (term & health) pre-loaded
Content Library	4 detailed guides (28KB of insurance knowledge)
Modern UI	Clean chat interface with quick actions
🚀 To Run
cd nyvo-chatbot

# 1. Setup
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 2. Run
./run.sh

# Or manually:
pip install -r requirements.txt
python scripts/seed_data.py
python -m app.main
Then open frontend/index.html or visit http://localhost:8000/docs for API docs.

🔌 Key APIs
POST /api/v1/chat — Main conversation endpoint
POST /api/v1/recommend/health — Health insurance recommendations
POST /api/v1/recommend/term — Term insurance recommendations
POST /api/v1/content/ingest — Index content library
Want me to add anything else — authentication, more policy data, or WhatsApp/Telegram integration?

Assistant
11:34
U
System: [2026-01-29 11:50:13 GMT+5:30] Exec failed (amber-sh, signal SIGKILL) :: ev > next dev ▲ Next.js 16.1.6 (Turbopack) - Local: http://localhost:3000 - Network: http://192.168.88.32:3000 ✓ Starting... ✓ Ready in 561ms GET / 200 in 719ms (compile: 525ms, render: 194ms) GET /health-insurance 200 in 62ms (compile: 43ms, render: 19ms) GET / 200 in 129ms (compile: 6ms, render: 123ms) GET /health-insurance/companies 200 in 80ms (compile: 56ms, render: 25ms)

How to add data for the bot?

You
11:50
A

There are two ways to add data to the bot:

1. Knowledge Base (Educational Content)
Add markdown/text files to nyvo-chatbot/nyvo-content/:

# Add your content files
nyvo-chatbot/nyvo-content/
├── health-insurance-basics.md    # Already included
├── term-insurance-guide.md       # Already included
├── your-new-content.md           # Add new files here
└── company-specific/
    ├── hdfc-products.md
    └── icici-products.md
Then re-index by calling the API:

curl -X POST http://localhost:8000/api/v1/content/ingest
2. Policy Database (For Recommendations)
Edit the seed script or add policies directly to the database.

Option A: Edit the seed script

read
nyvo-chatbot/scripts/seed_data.py:60-110
Completed