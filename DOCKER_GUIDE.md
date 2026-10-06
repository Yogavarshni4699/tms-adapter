# Docker Guide

## Quick Start

### Build Production Image

```bash
docker build -t tms-adapter:latest .
```

### Build Test Image

```bash
docker build -f Dockerfile.test -t tms-adapter:test .
```

### Run with Docker Compose

```bash
# Start adapter
docker-compose up -d tms-adapter

# Run tests
docker-compose --profile test up tms-tests

# View logs
docker-compose logs -f tms-adapter

# Stop
docker-compose down
```

## Environment Variables

Create `.env` file:

```
TMS_HOST=tramway.proxy.rlwy.net
TMS_PORT=17159
TMS_TOKEN=your_token
FMCSA_WEB_KEY=your_key
```

## Images

- **Production** — `python:3.14-slim` with TMS client (~150 MB)
- **Test** — Includes pytest with coverage reporting (~200 MB)

## Health Checks

Production image includes DEBUG_ECHO health check:

```bash
docker inspect --format='{{.State.Health.Status}}' happyrobot-tms-adapter
```

## Running Tests

```bash
docker run --env-file .env tms-adapter:test
```

## Cleanup

```bash
docker rmi tms-adapter:latest tms-adapter:test
docker-compose down -v
```
