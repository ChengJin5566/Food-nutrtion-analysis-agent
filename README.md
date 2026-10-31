# Food Nutrition Agent
<img width="664" height="714" alt="image" src="https://github.com/user-attachments/assets/360a4f34-af09-4a4c-be88-3724f380621c" />


Send a photo of a meal on Telegram and get back its nutrition breakdown.

A vision AI model identifies the dish and its components with estimated portions. Each component is matched against the Malaysian Food Composition Database (MyFCD) or USDA, and the nutrients are calculated and totalled.

## How it fits together

```
Telegram photo ──► n8n (Docker) ──► Food agent API (FastAPI, port 8000) ──► nutrition JSON
                       ▲                                                        │
                       └──────── formats a readable Telegram message ◄──────────┘
```

- **`food_agent/` code (repo root)**: the Python service (`POST /analyze-food`).
- **`n8n/Food-analysis.json`**: the n8n workflow. It downloads the Telegram photo, sends it to the food agent at `http://host.docker.internal:8000/analyze-food`, and builds the reply message with totals. It is a sub-workflow (it starts with "When Executed by Another Workflow"), so a Telegram bot workflow calls it with a `file_id`.
- **`docker-compose.yml`**: runs n8n in Docker.

## 1. Run the food agent

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
playwright install chromium
cp .env.example .env            # add OPENROUTER_API_KEY and USDA_API_KEY
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Quick test: `POST http://localhost:8000/analyze-food` with a multipart field `file` containing an image.

## 2. Run n8n in Docker

```bash
docker compose up -d
```

Open http://localhost:5678, create the owner account, then **Workflows → Import from file** and choose `n8n/Food-analysis.json`.

`docker compose` pulls the official `n8nio/n8n` image from Docker Hub automatically.

## 3. Set up credentials in n8n

Credentials are not included in the export. Create a **Telegram** credential (bot token from @BotFather) and select it in the "Get a file" node.

To trigger the workflow, call it from a Telegram bot workflow (an "Execute Workflow" node or an agent tool) and pass the photo's `file_id`.

Telegram webhooks need a public HTTPS URL. Use a tunnel (ngrok/cloudflared) and set `WEBHOOK_URL` in `.env`.

## Files

| File | Purpose |
|------|---------|
| `api.py` | FastAPI endpoint |
| `main.py` | LangGraph agent: image → food components → nutrition |
| `select_food.py` | LLM picks the best database match for each component |
| `embedding_search.py` | Embedding-based candidate search |
| `food_database.py`, `Search_info.py` | MyFCD lookup and scraping |
| `USDA.py` | USDA FoodData Central lookup |
| `calculate_nutrition.py` | Scales nutrition by portion size |
| `n8n/Food-analysis.json` | n8n workflow (Telegram photo → API → formatted reply) |
| `docker-compose.yml` | n8n in Docker |

## Notes

- Never commit `.env` or API keys.
- Pin the n8n image version in `docker-compose.yml` so workflows keep working after updates.
