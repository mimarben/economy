# === Load .env ===
ifneq (,$(wildcard .env))
		include .env
		export
endif

# === Variables por defecto ===
BACKEND_DIR := api
FRONTEND_DIR := client

BACKEND_IMAGE ?= flask-dev
BACKEND_TAG ?= 1.0
BACKEND_PORT ?= 5001
BACKEND_FULL := $(BACKEND_IMAGE):$(BACKEND_TAG)

FRONTEND_IMAGE ?= angular-dev
FRONTEND_TAG ?= 1.0
FRONTEND_PORT ?= 4200
FRONTEND_FULL := $(FRONTEND_IMAGE):$(FRONTEND_TAG)

.PHONY: build-backend run-backend build-frontend run-frontend clean dev-up dev-down stop-backend stop-frontend

# === BACKEND ===
build-backend:
	@echo "🔧 Building backend image $(BACKEND_FULL)..."
	docker build -t $(BACKEND_FULL) $(BACKEND_DIR)

run-backend:
	@echo "🚀 Running backend container on port $(BACKEND_PORT)..."
	docker run  -d --name $(BACKEND_NAME) --rm -p $(BACKEND_PORT):$(BACKEND_PORT) --env-file .env $(BACKEND_FULL)

stop-backend:
	@echo "🛑 Stopping backend container..."
	docker stop $(BACKEND_NAME) 2>/dev/null || true
	docker rm $(BACKEND_NAME) 2>/dev/null || true

# === FRONTEND ===
build-frontend:
	@echo "🔧 Building frontend image $(FRONTEND_FULL)..."
	docker build -t $(FRONTEND_FULL) $(FRONTEND_DIR)

run-frontend:
	@echo "🚀 Running frontend container on port $(FRONTEND_PORT)..."
	docker run -d --name $(FRONTEND_NAME) --rm -p $(FRONTEND_PORT):$(FRONTEND_PORT) --env-file .env $(FRONTEND_FULL)

stop-frontend:
	@echo "🛑 Stopping frontend container..."
	docker stop $(FRONTEND_NAME) 2>/dev/null || true
	docker rm $(FRONTEND_NAME) 2>/dev/null || true

dev-up: run-backend run-frontend
	@echo "🧩 Backend and frontend running together"

dev-down: stop-backend stop-frontend
	@echo "🛑 Backend and frontend stopped"

dev-restart: dev-down dev-up
	@echo "🔄 Backend and frontend restarted"

dev-compose-up:
	@echo "🧩 Starting services with docker-compose..."
	docker compose up -d

dev-compose-down:
	@echo "🛑 Stopping services with docker-compose..."
	docker compose down

# === LIMPIEZA ===
clean:
	@echo "🧹 Removing stopped containers..."
	docker container prune -f
