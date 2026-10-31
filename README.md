# Food Nutrition Agent

A Python (FastAPI + LangGraph) telegram agent service that takes a food photo, identifies the dish and its components with a vision LLM, matches each component against the Malaysian Food Composition Database (MyFCD) and USDA, and returns the nutrition values.

<img width="846" height="863" alt="image" src="https://github.com/user-attachments/assets/3fb42bb4-bdd5-4a96-a5d9-fcd0967521b9" />

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
playwright install chromium
cp .env.example .env            # then add your keys
```

Required keys in `.env`:
- `OPENROUTER_API_KEY`
- `USDA_API_KEY`

## Run

```bash
uvicorn api:app --reload
```

Send an image with `POST http://localhost:8000/analyze-food` (multipart form field `file`).

## Files

| File | Purpose |
|------|---------|
| `api.py` | FastAPI endpoint |
| `main.py` | LangGraph agent: image → food components → nutrition |
| `select_food.py` | LLM picks the best database match for each component |
| `embedding_search.py` | Embedding-based candidate search |
| `food_database.py`, `Search_info.py` | MyFCD scraping and lookup |
| `USDA.py` | USDA FoodData Central lookup |
| `calculate_nutrition.py` | Scales nutrition by portion size |
