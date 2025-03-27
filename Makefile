.PHONY: docker-build docker-run docker-build-cuda docker-run-cuda docker-clean
default: help

CONTAINER_NAME:= hysds/isce2
MEMORY_LIMIT:= 16G

# --------------------
# Docker commands
# --------------------

docker-build:  ## Build the docker image
	docker build --rm --force-rm -t $(CONTAINER_NAME):latest -f docker/Dockerfile .

docker-build-cuda:  ## Build the docker image with CUDA support
	docker build --rm --force-rm -t $(CONTAINER_NAME):latest-cuda -f docker/Dockerfile.cuda .

docker-run:  ## Run the docker container
	docker run --rm -it --memory $(MEMORY_LIMIT) \
	-v $(shell pwd)/alos-data:/home/data \
	-v $(shell pwd)/results:/home/results \
	-v $(shell pwd)/xml:/home/xml \
	-v $(shell pwd)/netrc/.netrc:/root/.netrc:ro \
	$(CONTAINER_NAME):latest bash

docker-run-cuda:  ## Run the docker container with CUDA support
	docker run --gpus all --rm --memory $(MEMORY_LIMIT) \
	-v $(pwd)/alos-data:/home/data \
	-v $(pwd)/results:/home/results \
	hysds/isce2:latest-cuda bash

docker-clean:  ## Clean the docker image and containers
	docker rmi $(CONTAINER_NAME):latest

docker-ps:  ## List all docker containers regarding the ISCE2 project
	docker ps -a --filter ancestor=$(CONTAINER_NAME)

docker-stop:  ## Stop all docker containers regarding the ISCE2 project
	docker stop $(docker ps -a --filter ancestor=$(CONTAINER_NAME) --format "{{.ID}}")

docker-rm:  ## Remove all docker containers regarding the ISCE2 project
	docker rm $(docker ps -a --filter ancestor=$(CONTAINER_NAME) --format "{{.ID}}")

# --------------------
# ISCE2 commands
# --------------------

isce2-run:
	docker run --rm --memory $(MEMORY_LIMIT) \
	  -v $(PWD)/alos-data:/home/data \
	  -v $(PWD)/results:/home/results \
	  -v $(PWD)/xml:/home/xml \
	  -v $(HOME)/.netrc:/root/.netrc:ro \
	  isce2:latest /bin/bash -c "cd /home/results && stripmapApp.py /home/xml/alos2-Noto-insar.xml"

# Help
# --------------------

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'