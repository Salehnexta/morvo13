# Morvo AI Marketing Consultant

Enterprise-grade FastAPI-based SaaS application featuring CrewAI agents, A2A HTTP-only protocol, OpenAI integration, Celery, Redis, SQLAlchemy, and Supabase/Postgres.

## Overview

Morvo is an AI Marketing Consultant specifically for the Saudi market with cultural intelligence. It features:

- 11 specialized agents with Saudi cultural intelligence
- Multi-stage Arabic onboarding flow with cultural sensitivity
- Integration with Islamic values and Vision 2030 initiatives
- Perplexity AI for website analysis
- SE Ranking for competitor analysis
- Complete user journey from registration through advanced consultation

## Core Agents

1. **Master Agent**: Orchestrates other agents and manages the conversation flow
2. **Data Synthesis Agent**: Processes and combines data from multiple sources
3. **Cultural Context Agent**: Provides Saudi-specific cultural intelligence
4. **Perplexity Agent**: Analyzes websites and online content
5. **SE Ranking Processor Agent**: Performs competitor analysis

## Features

- **Enterprise-grade Security**: JWT authentication with scopes, rate limiting, CORS protection
- **Comprehensive Database Schema**: Enhanced user models, conversation tracking, analytics
- **Performance Optimization**: Redis caching, async processing, Celery task queue
- **Monitoring & Observability**: Prometheus metrics, error tracking, request tracing
- **Cultural Intelligence**: Saudi market expertise, Vision 2030 alignment, Islamic compliance

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Environment Setup

Copy the example environment file and update the values:

```bash
cp .env.example .env
```

### Running with Docker

```bash
docker-compose up -d
```

### Running Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run database migrations:

```bash
alembic upgrade head
```

3. Start the application:

```bash
uvicorn app.main:app --reload
```

## API Documentation

API documentation is available at `/api/v1/docs` when the server is running.

## Project Structure

```
├── app/
│   ├── api/              # API endpoints and dependencies
│   ├── agents/           # AI agent implementations
│   ├── core/             # Core functionality (config, security, etc.)
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # Application entry point
├── migrations/           # Alembic migrations
├── tests/                # Test suite
├── alembic.ini           # Alembic configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker build configuration
└── requirements.txt      # Python dependencies
```

## License

Proprietary - All rights reserved
