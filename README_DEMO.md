Run the demo

Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

Frontend

```bash
cd frontend
npm install
npm run dev
```

Demo steps

1. Open `http://localhost:5173`.
2. Click `Load Sample Repo`.
3. Click `Load Sample Contract`.
4. Click `Validate Contract`.
5. Inspect the generated validation summary and alerts.
