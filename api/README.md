# PND Agents Marketplace API

FastAPI-based backend for the PND Agents Marketplace.

## Overview

This API provides read-only access to agent metadata for the marketplace UI. It discovers agents by scanning `agent.yaml` files in the `src/agents/` directory and merges them with runtime configuration from `mcp-config/agents.config.json`.

## Quick Start

```bash
# From the api/ directory
pip install -e ".[dev]"

# Run the development server
uvicorn src.main:app --reload --port 8000
```

## API Endpoints

### Agents

- `GET /api/agents` - List all agents (with optional filtering)
- `GET /api/agents/{agent_id}` - Get agent details
- `GET /api/agents/{agent_id}/config` - Get merged runtime configuration

### Metadata

- `GET /api/categories` - List all agent categories
- `GET /api/tags` - List all agent tags

### Health

- `GET /api/health` - Health check

## Query Parameters

The `/api/agents` endpoint supports the following filters:

| Parameter | Description |
|-----------|-------------|
| `category` | Filter by category (e.g., "Development", "Quality") |
| `status` | Filter by status ("stable", "beta", "experimental") |
| `tag` | Filter by tag |
| `search` | Search in name and description |

## Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Architecture

```
api/
├── src/
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   └── agents.py        # Agent endpoints
│   ├── services/
│   │   └── agent_discovery.py  # Agent scanning and querying
│   ├── models/
│   │   └── agent.py         # Pydantic models
│   └── adapters/            # Future: Agent execution bridges
└── pyproject.toml
```

## Agent Metadata

Agents are discovered by scanning for `agent.yaml` files in `src/agents/*/`. See `schemas/agent.schema.yaml` for the full schema.
