# MetricMind — Agentic Semantic BI Engine

MetricMind lets a business user ask plain-English questions like *"Why did our margins drop?"* and get back a trustworthy, auditable answer — without the AI ever writing raw SQL or hallucinating numbers.

## The problem

Letting an LLM query a data warehouse directly leads to hallucinated joins, inconsistent metrics, and Finance/Sales seeing different numbers for the same thing. MetricMind solves this by forcing the AI to go through a **governed semantic layer** instead of touching SQL directly.

## Architecture
Snowflake (raw data)
→ dbt (staging + marts layers, governed margin formula)
→ Cube.dev (semantic layer — Revenue/Margin exposed as a strict API)
→ LangChain Agent (Python + Llama 3 via Groq)
→ FastAPI (wraps the agent as a REST API)
→ Next.js (chat UI with charts, tables, and API transparency)
## What each layer does

| Layer | Tool | Purpose |
|---|---|---|
| Data Lakehouse | Snowflake | Stores raw Olist e-commerce data |
| Data Modeling | dbt | Cleans raw data (staging) and defines governed business metrics like Margin (marts) |
| Semantic Layer | Cube.dev | Exposes Revenue/Margin/Margin % as a fixed API — the AI can only ask for pre-approved metrics, never write its own SQL |
| Agentic AI | LangChain + Groq (Llama 3) | Converts natural language into semantic API calls; classifies questions as simple vs investigative; auto-drills into root-cause breakdowns for "why" questions |
| Backend API | FastAPI | Exposes a single `POST /ask` endpoint; enforces cost governance (row limits, timeouts, rate limiting) |
| Frontend | Next.js + Tailwind + Recharts | Chat interface with data tables, bar charts, and a "View API Call" transparency button |

## Key features

- **Governed metrics**: Margin is defined exactly once, in dbt, as `Revenue − Shipping Cost`. Every tool downstream (Cube.dev, the agent, the UI) uses this same definition — no metric drift.
- **Multi-step reasoning**: Investigative questions (e.g. "why is margin low") automatically trigger a second, category-level breakdown query to find the root cause — without the user having to ask for it.
- **Cost governance**: every query is capped at 1,000 rows, times out after 10 seconds, and the API is rate-limited to 10 requests/minute.
- **Full transparency**: every response includes the exact Cube.dev query that was run, viewable directly in the UI.

## Project structure
├── models/ # dbt models (staging + marts)
├── ai_agent/ # Python backend — LangChain agent + FastAPI
│ ├── agent.py # Core agent logic: query generation, classification, root-cause reasoning
│ ├── api.py # FastAPI wrapper exposing POST /ask
├── frontend/ # Next.js chat UI
└── olist_dataset/ # Source CSVs (sampled Olist e-commerce dataset)
## Running it locally

**Backend:**
```bash
cd ai_agent
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn api:app --reload
```
Runs at `http://127.0.0.1:8000` — test at `/docs`.

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:3000`.

Set `frontend/.env.local`:
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
And `ai_agent/.env`:
CUBE_API_URL=<your Cube.dev REST API endpoint>
CUBE_API_TOKEN=<your Cube.dev API token>
GROQ_API_KEY=<your Groq API key>
## Example queries to try

- "What is our total revenue by order status?"
- "What is our margin percentage by product category?"
- "Why is our margin so low overall?" — triggers automatic root-cause investigation

## Known limitation

Margin is approximated as `Revenue − Shipping Cost`, since true product cost (COGS) data is not available in the Olist dataset. This is documented explicitly rather than treated as ground truth — a deliberate, disclosed simplification, in keeping with the project's governance-first philosophy.