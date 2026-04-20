Explain My System — POC

Quick start

1. Create and activate a Python venv

python -m venv .venv
source .venv/bin/activate

2. Install dependencies

pip install -r requirements.txt

3. Run the backend

uvicorn main:app --reload --port 8002

Endpoints

- POST /load-sample — loads a bundled sample repo into memory
- GET /files — list parsed files
- GET /file?path=<path> — returns file text and chunk summaries
- GET /summary — high-level summary of repo
- POST /ask { question } — conversational question about code

Demo (curl)

# load sample
curl -X POST http://localhost:8002/load-sample

# list files
curl http://localhost:8002/files

# ask
curl -s -X POST http://localhost:8002/ask -H 'Content-Type: application/json' -d '{"question":"What does the app do?"}'

Notes

- The POC uses OpenAI embeddings + chat if OPENAI_API_KEY is set. Otherwise it falls back to a TF-IDF retriever.
- Storage is in-memory for simplicity.
