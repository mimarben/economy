# === Load docker.env ===
ifneq (,$(wildcard docker.env))
    include docker.env
    export
endif

# Variables por defecto
IMAGE_NAME ?= flask-dev
IMAGE_TAG ?= 1.0
FULL_IMAGE_NAME = $(IMAGE_NAME):$(IMAGE_TAG)
PORT := $(or $(PORT),5001)


.PHONY: build run docker

# Construye la imagen Docker
build:
	@echo "Building Docker image $(FULL_IMAGE_NAME)..."
	docker build -t $(FULL_IMAGE_NAME) .

# Arranca el contenedor Docker
run:
	@echo "Running Docker container on port $(PORT)..."
	docker run --rm -p $(PORT):$(PORT) --env-file docker.env $(FULL_IMAGE_NAME)

# Construye y arranca
docker: build run

