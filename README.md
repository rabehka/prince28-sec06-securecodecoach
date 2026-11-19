[![CI](https://github.com/rabehka/prince28-sec06-securecodecoach/actions/workflows/ci.yml/badge.svg)](https://github.com/rabehka/prince28-sec06-securecodecoach/actions)


# SecureCodeCoach

**An AI-powered secure coding mentor that helps developers identify vulnerabilities and learn safer coding practices using OWASP guidance.**

## 1. Target Users

- Beginner software developers
- Computer science students
- Programmers learning secure coding
- Developers who want to improve application security

## 2. Problem Statement

Developers may write code without identifying security vulnerabilities. This can lead to SQL Injection, Cross-Site Scripting (XSS), insecure authentication, and other security risks.

SecureCodeCoach aims to help developers understand common vulnerabilities and follow secure coding practices through AI-powered explanations and OWASP-based guidance.

## 3. Data Sources

The project uses:

- OWASP Top 10 security guidance
- Sample security vulnerability records stored in `data/sample_records.json`
- Security information and examples used for learning and testing

## 4. Project Goals

- Identify common security vulnerabilities.
- Explain security risks in simple language.
- Provide OWASP-based secure coding guidance.
- Help developers improve their coding practices.
- Build a reliable backend using FastAPI.

## 5. Technology Stack

- Python 3.12
- FastAPI
- Pydantic Settings
- uv
- Pytest
- Ruff
- JSON

## 6. Hardest Problem

One of the challenging parts is building a reliable backend that loads security records correctly and handles errors safely.

Implementing request ID tracking and structured JSON logging is also important for debugging and monitoring API requests.

## 7. Target Metrics

- At least 20 security records in the dataset.
- All API endpoints should return the expected responses.
- At least 6 automated API tests should pass.
- Invalid requests should return proper HTTP error responses.
- Every application request log should include a unique `request_id`.
- Normal API requests should complete within 2 seconds.

## 8. Project Structure

```text
securecodecoach/
│
├── data/
│   └── sample_records.json
│
├── docs/
│   ├── QUESTIONS.md
│   └── REQUIREMENTS.md
│
├── src/
│   └── securecodecoach/
│       ├── api/
│       │   ├── routes/
│       │   │   ├── documents.py
│       │   │   └── health.py
│       │   └── main.py
│       ├── config.py
│       ├── data_loader.py
│       └── logging_setup.py
│
├── tests/
│   ├── test_api.py
│   ├── test_data_loader.py
│   └── test_health.py
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```

## 9. Getting Started

### Prerequisites

- Python 3.12
- uv package manager

### Step 1: Clone the repository

```bash
git clone https://github.com/rabehka/prince28-sec06-securecodecoach.git
cd prince28-sec06-securecodecoach
```

### Step 2: Install dependencies

```bash
uv sync
```

### Step 3: Configure environment variables

Copy `.env.example` to `.env` and configure the required values.

Example:

```env
APP_NAME=securecodecoach
APP_ENV=local
LOG_LEVEL=INFO
DATA_FILE=data/sample_records.json
```

Never commit your actual `.env` file or API keys.

### Step 4: Run the application

```bash
uv run uvicorn securecodecoach.api.main:app --reload --no-access-log
```

### Step 5: Open API documentation

Visit:

http://127.0.0.1:8000/docs

## 10. Available API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/v1/documents` | Get all security records |
| GET | `/v1/documents/{document_id}` | Get a record by ID |

## 11. Testing

Run automated tests:

```bash
uv run pytest
```

Run Ruff checks:

```bash
uv run ruff check .
```

## 12. Current Project Status

- FastAPI backend implemented.
- Environment-based configuration implemented.
- Structured JSON logging implemented.
- Request ID tracking implemented.
- Problem Details error responses implemented.
- Health and readiness endpoints implemented.
- Security document endpoints implemented.
- 20 sample security vulnerability records added.
- Automated tests passing.

---

**Project:** SecureCodeCoach
**Repository:** https://github.com/rabehka/prince28-sec06-securecodecoach

## 13. Running with Docker & Docker Compose

Start PostgreSQL, Redis, and the FastAPI service (which runs Alembic migrations and loads initial records automatically):

```bash
docker compose up -d --build
```

Check container health:

```bash
docker compose ps
curl [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)
```

## 14. Unit vs. Integration Tests & Coverage

- **Unit tests** (fast, zero database dependency):
  ```bash
  uv run pytest tests/unit
  ```
- **Integration tests** (runs against an isolated `securecodecoach_test` database and drops it afterward):
  ```bash
  uv run pytest tests/integration
  ```
- **Full suite with coverage report:**
  ```bash
  uv run pytest -v --cov=securecodecoach --cov-report=term-missing
  ```

## Run locally in one command

You need Docker Desktop running. From a fresh clone:

```bash
docker compose up --build
```

This starts Postgres (with pgvector), Redis, runs the migrations and loads the sample data once, then starts the API.

- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/health
- Readiness (checks the database): http://localhost:8000/ready

Stop with `Ctrl+C`, then `docker compose down`. Add `-v` to also delete the database volume.

## Develop and test

| Task | Mac / Linux | Windows |
|---|---|---|
| Run the API with reload | `make dev` | `uv run poe dev` |
| Unit tests (no network) | `make test` | `uv run poe test` |
| Integration tests (needs `docker compose up`) | `make test-integration` | `uv run poe test-integration` |
| Coverage report | `make cov` | `uv run poe cov` |
| Lint and format check | `make lint` | `uv run poe lint` |
