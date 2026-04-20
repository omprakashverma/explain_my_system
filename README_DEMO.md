Run the POC demo

Backend

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

Frontend

cd frontend
npm install
npm run dev
# open http://localhost:5173

Then use the UI to load sample, list files, and ask questions.
