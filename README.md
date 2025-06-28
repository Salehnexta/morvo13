# Morvo AI Backend

[![CI](https://github.com/Salehnexta/morvo13/actions/workflows/ci.yml/badge.svg)](https://github.com/Salehnexta/morvo13/actions/workflows/ci.yml)
[![Docker Image](https://img.shields.io/badge/ghcr-image-blue)](https://github.com/Salehnexta/morvo13/pkgs/container/morvo13)

Enterprise-grade AI marketing platform powered by agentic workflows.

---

## Local Development

```bash
# spin up full stack (app + postgres + redis)
docker compose up --build
```

The API will be available at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

## Continuous Integration

All pushes & pull-requests trigger the GitHub Actions [CI workflow](.github/workflows/ci.yml) which runs:

* Ruff (lint)
* mypy (type-check)
* pytest with coverage (>80% enforced)
* Docker build (main branch) → pushes to GHCR

## Deployment (Render)

The included [`render.yaml`](render.yaml) automatically provisions:

* A **Web Service** for the FastAPI backend
* A **Background Worker** for Celery
* A **PostgreSQL** database & **Redis** instance

Simply import the repo in Render, set the required environment variables and you're live.

## Environment Variables

See [`env.example`](env.example) for the full list; at minimum you'll need:

* `OPENAI_API_KEY`
* `DATABASE_URL`
* `REDIS_URL`
* `SECRET_KEY`
* `SENTRY_DSN` (optional)

## License

MIT © Morvo
