lint:
	@docker run --rm -e RUN_LOCAL=true -v $(shell pwd):/tmp/lint github/super-linter:v4
