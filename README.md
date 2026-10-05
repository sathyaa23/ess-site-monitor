# ESS Site Monitor

A FastAPI service that validates battery **Energy Storage System (ESS)** telemetry
readings — voltage, temperature, and state of charge — and flags anomalies by
severity. Built as a testing + CI/CD reference project modeling the kind of
monitoring software used to watch grid-scale battery sites.

---

## What it does

A battery site sends a telemetry reading. The service validates it against safe
operating ranges, classifies severity (ok / warning / critical), rejects
anomalous readings, and stores valid ones. A minimal dashboard lets you submit
readings through a browser.

```
reading → validate → classify severity → reject (422) or store (201)
```

## Architecture

```
app/
  validators.py   Pure validation functions (unit-tested in isolation)
  main.py         FastAPI app: /telemetry, /health, /dashboard, /docs

tests/
  unit/           pytest tests on pure logic          (many, fast)
  integration/    TestClient tests on the API          (fewer)
  e2e/            Playwright browser tests             (few, slow)
  selenium/       Selenium browser tests (same flows)  (few, slow)

Dockerfile        Multi-stage build + healthcheck
.github/workflows/ci.yml   Full CI/CD pipeline
```

## The test pyramid (why the layers)

| Layer | Tool | What it catches | Speed |
|-------|------|-----------------|-------|
| Unit | pytest | Wrong logic in a single function | Fast |
| Integration | TestClient | Broken wiring between endpoint + logic + store | Medium |
| E2E | Playwright / Selenium | Broken user-facing flow (UI → API → UI) | Slow |

## Running it

```bash
# 1. Install
pip install -r requirements.txt
playwright install chromium

# 2. Run the fast tests (no server needed)
pytest tests/unit tests/integration -v

# 3. Run the app
uvicorn app.main:app --reload
#   → http://localhost:8000/dashboard   (UI)
#   → http://localhost:8000/docs        (Swagger)

# 4. Run the browser tests (needs the app running in another terminal)
pytest tests/e2e -v          # Playwright
pytest tests/selenium -v     # Selenium

# 5. Build the Docker image
docker build -t ess-site-monitor .
docker run -p 8000:8000 ess-site-monitor

# 6. Build the Python package artifact
python -m build              # → dist/*.whl and dist/*.tar.gz
```

## How this maps to the SQA role

| JD requirement | Where it lives here |
|----------------|---------------------|
| Develop/maintain **unit + integration tests** | `tests/unit/`, `tests/integration/` |
| **Frontend testing** (Selenium and Playwright) | `tests/e2e/` (Playwright), `tests/selenium/` (Selenium) |
| Debug: **identify, reproduce, resolve** issues | See `docs/BUGFIX.md` |
| **CI/CD pipelines** (GitHub Actions) | `.github/workflows/ci.yml` |
| **Package code** (Docker images, Python packages) | `Dockerfile`, `pyproject.toml` |
| **AWS** (S3, EC2, IAM) | See `docs/AWS_DEPLOY.md` (deploy-ready) |
| **Git branching + PRs + merge conflicts** | See `docs/GIT_WORKFLOW.md` |
| **Agile ceremonies** | Team process — spoken to from prior experience |

See `docs/TALKING_POINTS.md` for honest, per-component interview notes.
