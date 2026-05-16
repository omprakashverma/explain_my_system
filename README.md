# Explain My System — AI for Codebase Understanding

[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb?style=flat-square)](#tech-stack)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)](#tech-stack)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)](#installation-guide)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=flat-square)](#installation-guide)
[![Architecture](https://img.shields.io/badge/Architecture-Agent--Ready-5B6CFF?style=flat-square)](#architecture-overview)

Explain My System is an AI-assisted platform for understanding software repositories faster. It helps developers, architects, reviewers, and hackathon teams load a codebase, inspect files, explore structure, and ask contextual questions using repository-aware AI workflows.

---

## Project Overview

Modern codebases are difficult to understand because knowledge is fragmented across services, folders, files, frameworks, and undocumented team conventions. New contributors often spend hours reconstructing system behavior from raw source code before they can make safe changes.

Explain My System addresses that problem by combining:

- repository ingestion from ZIP, Git, or sample projects
- file-level code indexing and lightweight retrieval
- AI-ready prompt enrichment using repository and file context
- a clean UI for exploring source code and saving collaborative notes
- a modular architecture designed for future agentic AI workflows

The result is a practical developer experience for quickly answering questions like:

- What does this repository do?
- Which files matter most?
- What API routes exist?
- What does this selected file implement?
- What questions has the team already tagged on this file?

---

## Key Features

- Repository upload via ZIP archive
- Git repository cloning and indexing
- AI-powered repository Q&A
- File-level contextual AI understanding
- Repository-wide semantic-search-ready retrieval foundation
- Source explorer for indexed files
- Raw code preview with line numbers
- File notes for collaborative review and handoff
- Repository summary with detected languages, routes, and top modules
- AI architecture understanding placeholders for future analysis agents
- Modular React and FastAPI architecture
- Agent-ready backend structure for orchestration and future RAG workflows

---

## Architecture Overview

The platform is split into a modular frontend and backend with clear boundaries between UI rendering, state management, API integration, repository analysis, and AI orchestration.

### High-Level Architecture

```text
+---------------------+        HTTP/JSON        +----------------------+
| React Frontend      |  <------------------>   | FastAPI Backend      |
| - Dashboard UI      |                         | - API Routes         |
| - Hooks/Context     |                         | - Services           |
| - API Services      |                         | - Models             |
| - Reusable Panels   |                         | - In-Memory Store    |
+---------------------+                         +----------+-----------+
                                                          |
                                                          v
                                            +--------------------------+
                                            | Repository Processing    |
                                            | - ZIP ingestion          |
                                            | - Git clone              |
                                            | - File indexing          |
                                            | - Chunk generation       |
                                            | - Route extraction       |
                                            +------------+-------------+
                                                         |
                                                         v
                                            +--------------------------+
                                            | AI Orchestration Layer   |
                                            | - Context builder        |
                                            | - Q&A agent              |
                                            | - LLM service            |
                                            | - Future agent adapters  |
                                            +--------------------------+
```

### Frontend

- Built with React functional components
- Uses hooks and context for state orchestration
- Separates UI, API access, and reusable logic
- Presents repository loading, preview, Q&A, and notes in focused workspaces

### Backend

- Built with FastAPI and modular route registration
- Uses Pydantic request/response models
- Encapsulates repository loading, file access, note handling, parsing, summary generation, and AI calls in services
- Exposes a stable API contract for the React client

### AI Orchestration Layer

- Prepares file-specific and repository-wide context before AI calls
- Supports OpenAI-compatible chat completion APIs
- Is structured to evolve into streaming, agentic, and RAG-enabled workflows

### Repository Indexing and File Analysis Flow

1. Load repository from ZIP, Git, or sample source
2. Filter supported code files
3. Normalize and store file contents
4. Chunk files for retrieval and prompt context
5. Extract route metadata and build repository summary
6. Serve file preview, notes, and AI question-answering endpoints

### Future Agentic AI Support

The backend already includes placeholders and extension points for:

- `RepositoryAgent`
- `QAAgent`
- `ArchitectureAnalysisAgent`
- `DependencyAnalysisAgent`
- `DocumentationAgent`

This makes the system a strong foundation for multi-agent workflows, vector retrieval, and advanced code intelligence.

---

## UI/UX Overview

The UI is designed as a practical engineering workspace rather than a generic chatbot.

### Repository Loader

- Upload a ZIP
- Clone a Git repository
- Load a bundled sample repository
- Clear current state

### Repository Summary

- Shows repository source, file count, language count, route count, and overall status
- Displays top modules detected during indexing

### Source Explorer

- Lists all indexed files
- Lets users move quickly through repository structure

### File Preview

- Renders raw source code with line numbers
- Highlights context for file-specific analysis workflows

### AI Q&A Workspace

- Accepts repository questions
- Uses selected file context when available
- Returns AI answers or configuration feedback when no LLM is set

### Notes Workspace

- Saves file-specific questions/notes
- Supports collaborative context for code review and onboarding

---

## Folder Structure

### Frontend

```text
frontend/
├── index.html
├── package.json
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── style.css
│   ├── components/
│   │   ├── common/
│   │   ├── layout/
│   │   ├── notes/
│   │   ├── preview/
│   │   ├── qa/
│   │   ├── repository/
│   │   └── status/
│   ├── context/
│   │   └── AppContext.jsx
│   ├── hooks/
│   │   ├── useAskAI.js
│   │   ├── useFilePreview.js
│   │   ├── useNotes.js
│   │   └── useRepository.js
│   ├── pages/
│   │   └── Dashboard/
│   ├── services/
│   │   ├── aiService.js
│   │   ├── apiClient.js
│   │   ├── fileService.js
│   │   ├── noteService.js
│   │   └── repositoryService.js
│   ├── types/
│   └── utils/
└── dist/
```

### Backend

```text
backend/
└── app/
    ├── main.py
    ├── api/
    │   ├── router.py
    │   └── routes/
    │       ├── ask.py
    │       ├── files.py
    │       ├── health.py
    │       ├── notes.py
    │       └── repository.py
    ├── agents/
    │   ├── architecture_agent.py
    │   ├── dependency_agent.py
    │   ├── documentation_agent.py
    │   ├── qa_agent.py
    │   └── repository_agent.py
    ├── core/
    │   ├── config.py
    │   ├── constants.py
    │   └── logging.py
    ├── models/
    │   ├── request_models.py
    │   └── response_models.py
    ├── services/
    │   ├── ai_service.py
    │   ├── file_service.py
    │   ├── note_service.py
    │   ├── parser_service.py
    │   ├── repository_service.py
    │   └── summary_service.py
    ├── storage/
    │   └── repository_store.py
    └── utils/
        ├── file_utils.py
        ├── git_utils.py
        └── text_utils.py
```

---

## Tech Stack

### Frontend

- React
- Vite
- Axios

### Backend

- FastAPI
- Python
- Pydantic

### AI / Platform

- OpenAI-compatible chat completion architecture
- RAG-ready retrieval and context-building foundation
- Agent-ready service and orchestration layer

---

## Installation Guide

### Prerequisites

- Node.js `18+`
- Python `3.10+`
- Git installed locally

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL:

```text
http://localhost:5173
```

### Backend Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Run the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

Backend default URL:

```text
http://localhost:8002
```

---

## Environment Variables

Create a `.env` file in the project root if you want to enable AI responses through an external LLM.

```bash
LLM_API_URL=https://api.groq.com/openai/v1/chat/completions
LLM_API_KEY=your_api_key_here
LLM_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
```

Frontend environment variables can be provided through Vite:

```bash
VITE_API_BASE=http://localhost:8002
```

### Variable Reference

| Variable | Required | Description |
|---|---:|---|
| `LLM_API_URL` | No | OpenAI-compatible chat completions endpoint |
| `LLM_API_KEY` | No | API key for the configured LLM provider |
| `LLM_MODEL` | No | Model identifier used by the backend AI service |
| `VITE_API_BASE` | No | Frontend API base URL override |

If `LLM_API_KEY` is not set, the AI endpoints still function structurally but return a helpful configuration message instead of a live model response.

---

## API Documentation

Base URL:

```text
http://localhost:8002
```

### `GET /summary`

Returns the current repository summary.

**Example response**

```json
{
  "status": "ready",
  "overview": "Detected 2 files across 1 language(s). Found 4 route(s) in the repository.",
  "file_count": 2,
  "language_count": 1,
  "endpoint_count": 4,
  "source_type": "sample",
  "source_label": "Bundled sample repository",
  "loaded_at": "2026-05-14T16:01:31.264920",
  "top_modules": ["sample_api", "sample_app"],
  "top_files": ["sample_api.py", "sample_app.py"],
  "frameworks_detected": ["python"]
}
```

### `GET /files`

Returns indexed repository file paths.

**Example response**

```json
{
  "files": ["sample_api.py", "sample_app.py"]
}
```

### `GET /file`

Returns the raw file content, retrieval chunks, and notes for a given path.

**Example request**

```http
GET /file?path=sample_api.py
```

**Example response**

```json
{
  "path": "sample_api.py",
  "text": "from fastapi import APIRouter, FastAPI ...",
  "chunks": [
    {
      "path": "sample_api.py",
      "idx": 0,
      "text": "from fastapi import APIRouter, FastAPI ..."
    }
  ],
  "questions": [
    {
      "username": "qa",
      "question": "What does this do?",
      "timestamp": "2026-05-14T16:01:31.274872"
    }
  ]
}
```

### `POST /upload-zip`

Loads a ZIP archive and indexes supported source files.

**Example**

```bash
curl -X POST http://localhost:8002/upload-zip \
  -F "file=@repo.zip"
```

**Example response**

```json
{
  "files": 2,
  "chunks": 2,
  "source_type": "zip",
  "source_label": "repo.zip"
}
```

### `POST /load-git`

Clones a Git repository and indexes supported files.

**Example**

```bash
curl -X POST "http://localhost:8002/load-git?url=https://github.com/example/repo.git"
```

**Example response**

```json
{
  "files": 42,
  "chunks": 88,
  "source_type": "git",
  "source_label": "https://github.com/example/repo.git"
}
```

### `POST /load-sample`

Loads the bundled sample repository for demos.

**Example response**

```json
{
  "files": 2,
  "chunks": 2,
  "source_type": "sample",
  "source_label": "Bundled sample repository"
}
```

### `POST /clear`

Clears all in-memory repository state.

**Example response**

```json
{
  "cleared": true
}
```

### `POST /ask`

Asks a repository-level or file-level question.

**Example request**

```json
{
  "prompt": "What does this file do?",
  "selected_file": "sample_api.py"
}
```

**Example response**

```json
{
  "answer": "LLM is not configured. Set LLM_API_KEY to enable repository Q&A and summaries.",
  "found": 1,
  "selected_file": "sample_api.py"
}
```

### `POST /tag-question`

Stores a file-level note or question.

**Example request**

```json
{
  "path": "sample_api.py",
  "username": "Alice",
  "question": "Why is this endpoint here?"
}
```

**Example response**

```json
{
  "success": true,
  "file": "sample_api.py",
  "total_tags": 1
}
```

---

## AI Workflow Explanation

The current AI workflow follows a clear enrichment pipeline:

### 1. Repository Ingestion

- Load repository from ZIP, Git, or sample source
- Keep only supported code files

### 2. File Indexing

- Normalize paths
- Store file contents in memory
- Create retrieval chunks for contextual lookup

### 3. Context Extraction

- If a file is selected, build prompt context from the full file plus related chunks
- If no file is selected, retrieve repository-wide matching chunks

### 4. Prompt Enrichment

- Add system instructions for architecture-aware, file-aware answers
- Combine user prompt and repository context

### 5. AI Response Generation

- Send enriched messages to an OpenAI-compatible provider
- Return the generated answer to the frontend
- Fall back gracefully if the LLM is not configured

---

## Future Roadmap

- Multi-agent repository workflows
- Architecture diagram generation
- Dependency graph visualization
- AI impact analysis for code changes
- Security analysis agent
- Pull request review agent
- Incident investigation agent
- Vector database integration
- Streaming AI responses
- Persistent workspace memory
- Multi-user collaboration

---

## Testing Instructions

### Frontend Testing

```bash
cd frontend
npm install
npm run dev
```

Validate:

- repository loader
- file explorer
- file preview
- ask workspace
- notes workspace
- error states

### Backend Testing

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8002
```

Validate:

- startup and imports
- route registration
- CORS behavior
- happy-path API flows
- invalid-input responses

### End-to-End Validation

Recommended flow:

1. Load sample repository
2. Open a file from the explorer
3. Ask a file-level question
4. Save a note to the file
5. Upload a ZIP repository
6. Load a Git repository
7. Clear state and verify reset behavior

---

## Production Improvements

To move this from demo-ready to production-grade, the next steps should include:

- authentication and session management
- database persistence for repository state and notes
- caching for repository analysis and repeated AI calls
- WebSocket or SSE streaming for long-running AI responses
- role-based access control (RBAC)
- observability with metrics, tracing, and structured logs
- background job processing for large repositories
- vector search for true semantic retrieval at scale

---

## Contributing Guide

### Branching Strategy

- `main` for stable demo-ready code
- feature branches for scoped work
- small PRs preferred over large monolithic changes

### Coding Standards

- keep components and services modular
- prefer explicit naming over clever abstractions
- preserve current API contracts unless versioning is introduced
- add typing and schema clarity wherever possible
- keep UI and business logic separated

### Architecture Expectations

- frontend logic belongs in hooks/services, not giant page files
- backend routes should stay thin and delegate to services
- shared helpers should live in `utils`
- new AI capabilities should integrate through the service/agent layers

---

## License

Add your preferred project license here, such as MIT, Apache-2.0, or a hackathon/demo-specific license statement.

---

## Acknowledgements

- React and Vite for a fast frontend development experience
- FastAPI for ergonomic, high-performance Python APIs
- Pydantic for request and response modeling
- OpenAI-compatible LLM ecosystems for flexible AI integration
- The broader developer tooling community building better ways to understand code at scale

---

## Why This Project Matters

Explain My System is more than a chatbot for repositories. It is a practical foundation for AI-native software comprehension, onboarding acceleration, and architecture exploration. For judges, recruiters, engineering leaders, and developer platform teams, it demonstrates a clear direction: turning raw repositories into contextual, explainable, and agent-ready engineering workspaces.
