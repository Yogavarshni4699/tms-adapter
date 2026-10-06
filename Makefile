.PHONY: help build start stop restart test logs status clean ps

help:
	@echo "TMS Adapter - Make Commands"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make start      - Start adapter service"
	@echo "  make stop       - Stop adapter service"
	@echo "  make restart    - Restart adapter service"
	@echo "  make test       - Run test suite"
	@echo "  make logs       - View service logs"
	@echo "  make status     - Show container status"
	@echo "  make ps         - List containers (alias for status)"
	@echo "  make clean      - Remove all containers and volumes"
	@echo ""
	@echo "Examples:"
	@echo "  make build && make start"
	@echo "  make test"
	@echo "  make logs"

build:
	docker-compose build

start:
	docker-compose up -d tms-adapter
	@echo "✅ Service started"

stop:
	docker-compose stop tms-adapter
	@echo "✅ Service stopped"

restart:
	docker-compose restart tms-adapter
	@echo "✅ Service restarted"

test:
	docker-compose --profile test up --abort-on-container-exit tms-tests

logs:
	docker-compose logs -f tms-adapter

status:
	docker-compose ps

ps: status

clean:
	docker-compose down -v
	@echo "✅ Cleaned up"
