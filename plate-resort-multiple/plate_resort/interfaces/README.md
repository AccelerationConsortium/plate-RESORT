# PlateResort Interfaces

This directory contains the two main interface modes for the PlateResort system:

## Architecture Overview

```
plate_resort/
├── core.py                 # Shared motor control functionality
├── config/                 # Configuration system
├── utils/                  # Shared utilities
├── client/                 # Client-side tools
└── interfaces/             # Interface implementations
    ├── prefect/           # Modern workflow orchestration
    │   ├── flows.py       # Prefect flow definitions
    │   ├── orchestrator.py # Flow orchestration logic
    │   ├── deploy.py      # Deployment management
    │   └── worker_service.py # Prefect worker service
    └── rest_api/          # Traditional HTTP API
        ├── main.py        # FastAPI application
        └── wrapper.py     # REST endpoint wrapper
```

## Interface Modes

### Prefect Interface (`interfaces/prefect/`)
Modern cloud-native workflow orchestration using Prefect v3.

**Features:**
- Cloud-native workflow management
- Robust error handling and retries
- Remote deployment and monitoring
- Scalable task distribution
- Real-time logging and observability

**Console Scripts:**
- `plate-resort-prefect-interactive` - Interactive flow execution
- `plate-resort-prefect-worker` - Start Prefect worker service
- `plate-resort-prefect-deploy` - Deploy workflows to Prefect cloud

### REST API Interface (`interfaces/rest_api/`)
Traditional HTTP-based API server using FastAPI.

**Features:**
- Synchronous HTTP endpoints
- Direct motor control
- Simple request/response pattern
- API key authentication
- OpenAPI documentation

**Console Scripts:**
- `plate-resort-rest-server` - Start FastAPI server
- `plate-resort-rest-client` - Command-line REST client

## Choosing an Interface

**Use Prefect when:**
- Building complex automated workflows
- Need cloud connectivity and monitoring
- Require robust error handling and retries
- Working in production environments
- Need to coordinate multiple operations

**Use REST API when:**
- Building simple integrations
- Need direct synchronous control
- Prefer traditional HTTP patterns
- Working with existing REST-based systems
- Need immediate response feedback

Both interfaces share the same underlying `PlateResort` core functionality and configuration system.