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
- Supports both file-scoped and repository-scoped questions
- Uses selected file context when file scope is active
- Uses repository-wide retrieval when repository scope is active
- Offers predefined AI prompt templates for common repository analyses
- Returns AI answers or configuration feedback when no LLM is set

### Notes Workspace

- Saves file-specific questions/notes
- Supports repository-wide discussions and architecture questions
- Supports threaded replies with author and timestamp metadata
- Lets creators or admins mark questions resolved or reopen them
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
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8002
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
AUTH_DB_PATH=backend/app/storage/auth.db
AUTH_SESSION_DAYS=7
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
| `AUTH_DB_PATH` | No | SQLite database file used for users and sessions |
| `AUTH_SESSION_DAYS` | No | Number of days an authenticated session remains valid |
| `VITE_API_BASE` | No | Frontend API base URL override |

If `LLM_API_KEY` is not set, the AI endpoints still function structurally but return a helpful configuration message instead of a live model response.
The same SQLite database file is also used for tagged questions, replies, and resolution state.

---

## Authentication Flow

The application now requires authentication before repository features are available.

### Registration Flow

1. Open the frontend and switch to the `Register` tab.
2. Enter a username, optional email, and password.
3. Submit the form to create the account.
4. The backend hashes the password with PBKDF2 before storing it in SQLite.
5. After registration, the frontend stores the issued session token and opens the dashboard automatically.

### Login / Logout Usage

1. Use the `Login` tab with your username and password.
2. After login, the current username appears in the dashboard header and is used automatically for file notes.
3. Use the `Logout` button in the header to invalidate the current session and return to the auth screen.

### Protected Backend Behavior

- `GET /summary`, `GET /files`, `GET /file`, `POST /ask`, repository loading routes, and note creation now require a valid bearer token.
- `GET /health`, `POST /auth/register`, `POST /auth/login`, and `GET /auth/me` remain available for auth/bootstrap flows.

### Question Discussion Workflow

1. Choose whether the question should target a file or the whole repository.
2. Open a file and create a file-scoped tagged question, or stay in repository scope for a global discussion.
3. Any logged-in user can reply to the question.
4. The question author or an admin can mark it `Resolved` or switch it back to `Open`.
5. Replies and resolution state are stored in SQLite and scoped to the loaded repository and file path when applicable.

### Repository Question Workflow

1. Switch the ask panel to `Ask Entire Repository`.
2. The backend reuses the indexed repository snapshot, summary, file tree, and relevant chunks instead of rescanning the repo on every question.
3. The LLM receives a repository-aware prompt with structure metadata and cross-file snippets.
4. Repository discussions can be filtered separately from file discussions in the notes panel.

### Predefined Prompt Templates

The ask workspace now includes a prompt selector for common repository analyses such as:

- architecture overview
- API flow analysis
- authentication flow review
- frontend state and routing review
- security risk review
- code smell detection
- Mermaid architecture and class diagrams

Templates can either:

- apply their generated prompt into the manual input box, or
- run immediately against repository-wide context

## Admin Credentials

Username: admin
Password: admin123

The admin account is created automatically during backend startup if it does not already exist. The password is hashed before storage and is never hardcoded in the frontend source.

---

## API Documentation

Base URL:

```text
http://localhost:8002
```

### `POST /auth/register`

Creates a new user and returns a session token.

**Example request**

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "strongpass123"
}
```

### `POST /auth/login`

Authenticates an existing user and returns a session token.

**Example request**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### `POST /auth/logout`

Invalidates the current bearer token.

### `GET /auth/me`

Returns the currently authenticated user.

### `GET /summary`

Returns the current repository summary. Requires authentication.

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

Returns indexed repository file paths. Requires authentication.

**Example response**

```json
{
  "files": ["sample_api.py", "sample_app.py"]
}
```

### `GET /file`

Returns the raw file content, retrieval chunks, and notes for a given path. Requires authentication.

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

Loads a ZIP archive and indexes supported source files. Requires authentication.

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

Clones a Git repository and indexes supported files. Requires authentication.

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

Loads the bundled sample repository for demos. Requires authentication.

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

Clears all in-memory repository state. Requires authentication.

**Example response**

```json
{
  "cleared": true
}
```

### `POST /ask`

Asks a repository-level or file-level question. Searches tagged question history first before querying the LLM. Requires authentication.

**Example request**

```json
{
  "prompt": "What does this file do?",
  "selected_file": "sample_api.py",
  "scope": "FILE"
}
```

**Example response (from LLM)**

```json
{
  "answer": "LLM is not configured. Set LLM_API_KEY to enable repository Q&A and summaries.",
  "found": 1,
  "selected_file": "sample_api.py",
  "answer_source": "llm",
  "source_question_id": null,
  "related_questions": [
    {
      "question_id": 5,
      "question": "How does this API file structure work?",
      "username": "alice",
      "created_at": "2026-05-16T12:00:00+00:00",
      "scope": "FILE",
      "replies": [
        {
          "id": 12,
          "question_id": 5,
          "user_id": 2,
          "username": "bob",
          "content": "It follows a standard FastAPI router pattern...",
          "created_at": "2026-05-16T13:00:00+00:00"
        }
      ]
    }
  ]
}
```

**Example response (from history)**

```json
{
  "answer": "Based on previous discussion:\n\n**Q:** What does this file do?\n\n**Replies:**\nIt implements the API endpoints for authentication and user management.",
  "found": 1,
  "selected_file": "sample_api.py",
  "answer_source": "history",
  "source_question_id": 5,
  "related_questions": []
}
```

**Response Fields**

- `answer`: The answer text - either from a similar historical question or generated by the LLM
- `found`: Number of relevant chunks/questions found
- `selected_file`: The file that was queried (null for repository scope)
- `answer_source`: Either `"history"` (from tagged questions/replies) or `"llm"` (from AI model)
- `source_question_id`: If from history, the ID of the question that provided the answer
- `related_questions`: List of similar questions from team history, each containing:
  - `question_id`: Unique question identifier
  - `question`: The question text
  - `username`: User who asked the question
  - `created_at`: Timestamp of the question
  - `scope`: "FILE" or "REPOSITORY"
  - `replies`: Array of reply objects with author, content, and timestamp

**Behavior**

1. The system first searches through tagged questions for your current repository
2. If a very similar question is found (≥70% similarity), it returns that historical answer as the primary answer
3. Additionally, it returns related questions (50-70% similarity) that the team may have already discussed
4. If no good match is found, it queries the configured LLM
5. Users can see the answer source to distinguish between team knowledge and AI-generated responses

For repository-wide analysis, set `"scope": "REPOSITORY"` and omit `selected_file`.

### `GET /prompt-templates`

Returns the predefined prompt registry with template metadata, category, description, scope, and output format.

### `POST /prompt-templates/run`

Runs a predefined repository analysis template.

**Example request**

```json
{
  "template_id": "architecture_diagram"
}
```

### `GET /questions`

Lists tagged questions for the loaded repository. Requires authentication.

Supported query params:

- `scope=ALL`
- `scope=FILE`
- `scope=REPOSITORY`
- `path=<relative/file/path>` for file-level filtering

### `POST /tag-question`

Stores a file-level note or question. Requires authentication.

**Example request**

```json
{
  "path": "sample_api.py",
  "scope": "FILE",
  "question": "Why is this endpoint here?"
}
```

**Example response**

```json
{
  "success": true,
  "file": "sample_api.py",
  "total_tags": 1,
  "question": {
    "id": 1,
    "path": "sample_api.py",
    "scope": "FILE",
    "user_id": 2,
    "username": "alice",
    "question": "Why is this endpoint here?",
    "resolved": false,
    "resolved_at": null,
    "created_at": "2026-05-16T12:00:00+00:00",
    "reply_count": 0,
    "latest_reply_at": null,
    "replies": []
  }
}
```

### `GET /questions/{id}/replies`

Returns all replies for a tagged question.

### `POST /questions/{id}/reply`

Adds a reply to a tagged question. Requires authentication.

**Example request**

```json
{
  "content": "This endpoint exists for the health-check integration."
}
```

### `PATCH /questions/{id}/resolve`

Marks a question resolved or unresolved. Requires the question author or an admin.

**Example request**

```json
{
  "resolved": true
}
```

Repository-scoped questions can be created like this:

```json
{
  "path": null,
  "scope": "REPOSITORY",
  "question": "How does authentication flow through the whole application?"
}
```

---

## AI Workflow Explanation

The current AI workflow follows a clear enrichment pipeline with team knowledge prioritization:

### 1. Repository Ingestion

- Load repository from ZIP, Git, or sample source
- Keep only supported code files

### 2. File Indexing

- Normalize paths
- Store file contents in memory
- Create retrieval chunks for contextual lookup

### 3. Team Knowledge Search (NEW)

- When a question is asked, first search through tagged questions and replies from the team
- Calculate text similarity between the new question and historical questions (both file-scoped and repository-scoped)
- If a very similar question is found (≥70% similarity), use the historical Q&A as the primary answer
- Return related questions (50-70% similarity) that provide additional context
- This ensures team knowledge is prioritized over AI-generated responses

### 4. Context Extraction

- If a file is selected, build prompt context from the full file plus related chunks
- If repository scope is selected, build context from repository summary, file tree, and top relevant chunks across files
- If file scope is selected without a file, the API returns a validation error instead of guessing

### 5. Prompt Enrichment

- Add system instructions for architecture-aware, file-aware answers
- Include scope metadata, file paths, and cross-file snippets when repository scope is active
- Combine user prompt and retrieved repository context
- For predefined templates, inject richer analysis instructions from the centralized prompt registry

### 6. AI Response Generation

- If no historical answer was found, send enriched messages to an OpenAI-compatible provider
- Return the generated answer to the frontend
- Fall back gracefully if the LLM is not configured

### Performance Notes

- Repository files are indexed once when a repo is loaded.
- Lightweight chunk retrieval is reused for both file and repository scope.
- Large files are truncated during ingestion to keep context windows stable.
- Ignored folders include `node_modules`, `.git`, `dist`, `build`, and other generated paths.
- Historical question search uses word-overlap similarity for fast O(n) lookup without external dependencies.

### Diagram Support

- Diagram-oriented templates return Mermaid-first prompts so the LLM is nudged toward diagram code blocks.
- Current support is prompt-driven rather than rendered previews, which keeps the implementation lightweight and easy to extend.

### Answer Source Differentiation

Users can distinguish between answers in the UI:
- **📚 Team History**: Indicates the answer came from a previous team discussion about the same or similar topic
- **🤖 AI**: Indicates the answer was generated by the configured LLM model

Historical answers include links to the original question and all replies, making it easy for developers to understand the context and reasoning behind the answer.

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

- register a new user
- log in with the admin account
- confirm the dashboard header shows the logged-in username
- verify file-scope questions still require a selected file
- verify repository-scope questions work without a file selected
- verify repository-wide tags appear under repository discussions
- verify prompt templates load in the selector
- verify template apply and template run both work
- create a tagged question
- add replies from a logged-in account
- confirm resolve/unresolve changes the question badge
- repository loader
- file explorer
- file preview
- ask workspace
- notes workspace
- error states

### Backend Testing

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8002
```

Validate:

- startup and imports
- admin user auto-creation
- login, logout, and `/auth/me`
- repository-scope ask requests
- `GET /questions` scope filtering
- prompt template listing and execution
- reply creation and persistence
- creator/admin-only resolution permissions
- route registration
- CORS behavior
- happy-path API flows
- invalid-input responses

### End-to-End Validation

Recommended flow:

1. Start the backend and confirm the admin account is available
2. Register a new user from the frontend
3. Log out and log back in
4. Load the sample repository
5. Open a file from the explorer
6. Ask a file-level question
7. Switch to repository scope and ask an architecture-level question
8. Run a predefined architecture or security prompt template
9. Save a file-level note and a repository-level note
10. Add one or more replies
11. Mark the question resolved and then unresolved
12. Upload a ZIP repository
13. Load a Git repository
14. Clear state and verify reset behavior

---

## Production Improvements

To move this from demo-ready to production-grade, the next steps should include:

- database persistence for repository state
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
