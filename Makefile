IMAGE=iberdrola-distribucion-prometheus-exporter

lint:
	@docker run --rm -e RUN_LOCAL=true -v $(shell pwd):/tmp/lint github/super-linter:v4

build-local:
	@docker build --no-cache --pull -t $(IMAGE):local . -f build/container/Dockerfile
