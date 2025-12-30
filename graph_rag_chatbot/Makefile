.PHONY: build build-base build-services up down clean logs

# Build everything in correct order
build: build-base build-services

# Build base image first
build-base:
	docker build -t chatbot-base -f docker/base.Dockerfile .

# Build all service images (requires base to exist)
build-services:
	docker compose build backend database frontend

# Build and start all services
up: build
	docker compose up

# Start without rebuilding
start:
	docker compose up

# Stop all services
down:
	docker compose down

# Stop and remove volumes
clean:
	docker compose down -v --rmi local

# View logs
logs:
	docker compose logs -f

# Rebuild a specific service (e.g., make rebuild SERVICE=backend)
rebuild: build-base
	docker compose build $(SERVICE)
	docker compose up -d $(SERVICE)
