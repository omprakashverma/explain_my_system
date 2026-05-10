Explain My System - Smart API Contract Validator

This project now lets you:

1. Load a repository from a ZIP file, Git URL, or bundled sample repo.
2. Upload an OpenAPI contract in `.yaml`, `.yml`, or `.json`.
3. Validate the detected API routes in the loaded codebase against that contract.
4. Review mismatch alerts such as missing paths, method mismatches, and undocumented repo routes in the UI.

Quick start

1. Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install backend dependencies

```bash
pip install -r requirements.txt
```

3. Run the backend

```bash
uvicorn main:app --reload --port 8002
```

4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

5. Open `http://localhost:5173`

Suggested demo flow

1. Click `Load Sample Repo`.
2. Click `Load Sample Contract`.
3. Click `Validate Contract`.
4. Review the validator summary and any generated alerts.

Sample assets

- Sample API implementation: `sample/sample_api.py`
- Sample OpenAPI contract: `sample/sample_api_contract.yaml`

Key backend endpoints

- `POST /upload-zip` - load repository source files from a ZIP
- `POST /load-git?url=...` - clone and load a git repository
- `POST /load-sample` - load the bundled sample API repo
- `POST /upload-contract` - upload an OpenAPI contract file
- `POST /load-sample-contract` - load the bundled sample contract
- `POST /validate-contract` - compare the current repo against the loaded contract
- `GET /contract` - inspect the currently loaded contract metadata
- `GET /files` - list loaded source files
- `GET /file?path=...` - preview a source file
- `POST /ask` - ask questions about the loaded repository

Notes

- The contract validator currently recognizes common FastAPI, Flask, and Express-style route definitions.
- Contract parsing works with OpenAPI 3.x documents.
- Validation is route-level and focuses on path and HTTP method mismatches.
