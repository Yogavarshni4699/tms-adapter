# Container Management Guide

## Quick Start (Recommended)

Use `make` commands for easiest management:

```bash
# Build images
make build

# Start service
make start

# Run tests
make test

# Check status
make status

# View logs
make logs

# Stop service
make stop

# Clean up everything
make clean
```

## Docker Compose Method

Using docker-compose directly:

```bash
# Start services (creates or reuses containers)
docker-compose up -d tms-adapter

# Run tests
docker-compose --profile test up --abort-on-container-exit tms-tests

# Check running containers
docker-compose ps

# View logs
docker-compose logs -f tms-adapter

# Stop containers (keep them)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove, and delete volumes
docker-compose down -v
```

## Bash Script Method

Using the provided script:

```bash
# Make script executable (one time)
chmod +x scripts/compose.sh

# Use commands
./scripts/compose.sh start
./scripts/compose.sh test
./scripts/compose.sh logs
./scripts/compose.sh status
./scripts/compose.sh stop
./scripts/compose.sh clean
```

## Container Lifecycle

### Creating Containers
```bash
# First time (creates new containers)
make start
```

### Reusing Containers
```bash
# Restart existing container
make restart

# Stop (keeps container)
make stop

# Start again (reuses same container)
make start
```

### Cleaning Up
```bash
# Remove containers but keep images
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all
```

## Running Tests

### In existing container
```bash
make test
```

### With container logs
```bash
docker-compose --profile test logs -f tms-tests
```

### Get coverage report
```bash
make test
cat htmlcov/index.html
```

## Viewing Logs

### Follow live logs
```bash
make logs
```

### Show last 50 lines
```bash
docker-compose logs --tail=50 tms-adapter
```

### Show logs with timestamps
```bash
docker-compose logs -t tms-adapter
```

## Container Management

### Check what's running
```bash
make status
# or
docker-compose ps
```

### List all containers (including stopped)
```bash
docker ps -a | grep tms
```

### Remove specific container
```bash
docker-compose rm tms-adapter
```

### Inspect container
```bash
docker-compose exec tms-adapter sh
```

## Troubleshooting

### Port already in use
```bash
# Stop the container
make stop

# Check port usage
lsof -i :8000

# Or use different port in docker-compose.yml
```

### Container won't start
```bash
# Check logs
make logs

# Rebuild
make clean && make build && make start
```

### Tests fail in container but pass locally
```bash
# Rebuild without cache
docker-compose build --no-cache

# Check environment variables
docker-compose exec tms-tests env | grep TMS
```

### Disk space issues
```bash
# Remove all unused docker resources
docker system prune -a

# Remove volumes
docker volume prune
```

## Best Practices

1. **Always use docker-compose** - Consistent container management
2. **Use make commands** - Simple, memorable shortcuts
3. **Stop before removing** - `make stop` then `make clean`
4. **Check status first** - `make status` to see what's running
5. **Keep images small** - Use slim base images (already done)

## GitHub Actions Integration

CI/CD pipeline automatically:
- Builds containers
- Runs tests
- Cleans up after itself
- Uploads coverage reports

No manual container management needed in CI/CD - fully automated via `.github/workflows/docker-compose.yml`
