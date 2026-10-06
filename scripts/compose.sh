#!/bin/bash

set -e

COMMAND=${1:-help}

case $COMMAND in
  start)
    echo "Starting TMS adapter service..."
    docker-compose up -d tms-adapter
    echo "✅ Service started. Check status with: ./scripts/compose.sh status"
    ;;

  stop)
    echo "Stopping TMS adapter service..."
    docker-compose stop tms-adapter
    echo "✅ Service stopped"
    ;;

  restart)
    echo "Restarting TMS adapter service..."
    docker-compose restart tms-adapter
    echo "✅ Service restarted"
    ;;

  test)
    echo "Running tests..."
    docker-compose --profile test up --abort-on-container-exit tms-tests
    echo "✅ Tests completed"
    ;;

  logs)
    echo "Showing service logs..."
    docker-compose logs -f tms-adapter
    ;;

  status)
    echo "Container status:"
    docker-compose ps
    ;;

  clean)
    echo "Cleaning up containers and volumes..."
    docker-compose down -v
    echo "✅ Cleaned up"
    ;;

  build)
    echo "Building images..."
    docker-compose build
    echo "✅ Images built"
    ;;

  *)
    echo "TMS Adapter - Docker Compose Management"
    echo ""
    echo "Usage: ./scripts/compose.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start      - Start adapter service"
    echo "  stop       - Stop adapter service"
    echo "  restart    - Restart adapter service"
    echo "  test       - Run test suite"
    echo "  logs       - View service logs (follow mode)"
    echo "  status     - Show container status"
    echo "  clean      - Remove containers and volumes"
    echo "  build      - Build Docker images"
    echo ""
    echo "Examples:"
    echo "  ./scripts/compose.sh start"
    echo "  ./scripts/compose.sh test"
    echo "  ./scripts/compose.sh logs"
    ;;
esac
