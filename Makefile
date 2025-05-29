CONTAINER_ENGINE ?= $(shell which podman docker | head -n 1) 
ifndef CONTAINER_ENGINE
$(error CONTAINER_ENGINE is unset because it couldn't be auto-set; podman or docker missing from $$PATH. Skip this check with make CONTAINER_ENGINE=skip; but container commands will not work)
endif

include Makefile.devhelpers


.PHONY: clean
clean: pyproject.toml
	rm -rf .venv

.venv:
	@uv sync \
	--no-group check

.PHONY: sync
sync: .venv pyproject.toml

.PHONY: install
install:
	uv sync

.PHONY: check
check: flake8 pylint mypy

.PHONY: flake8
flake8: .venv
	@uv run                 \
	--quiet                \
	--isolated             \
	--group check          \
	flake8                 \
	dashdotdb

.PHONY: pylint
pylint: .venv
	@uv run                 \
	--quiet                \
	--isolated             \
	--group check          \
	pylint                 \
	dashdotdb


.PHONY: mypy
mypy: .venv
	@uv run                 \
	--quiet                \
	--isolated             \
	--group check          \
	mypy                   \
	--install-types        \
	--non-interactive      \
	--follow-untyped-imports

.PHONY: ci
ci:
	$(CONTAINER_ENGINE) build -t app-sre-dashdotdb-ci:do-not-use --target test -f Dockerfile .
	$(CONTAINER_ENGINE) build -t app-sre-dashdotdb:do-not-use --target prod -f Dockerfile .

test-data-imagemanifestvuln:
	@TOKEN="$$(curl --silent localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/token?scope=imagemanifestvuln | sed 's/"//g')" && \
	echo "imagemanifestvuln:" && \
	curl \
		-X POST \
		--header "Content-Type: application/json" \
		--header "X-Auth: $${TOKEN}" \
		--data @examples/imagemanifestvuln.json \
		localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/imagemanifestvuln/app-sre-prod-01 && \
	curl \
		--request DELETE \
		"localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/token/$${TOKEN}?scope=imagemanifestvuln"

test-data-serviceslometrics:
	@TOKEN=$$(curl --silent localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/token?scope=serviceslometrics | sed 's/"//g') && \
	echo "serviceslometrics:" && \
	curl \
		-X POST \
		--header "Content-Type: application/json" \
		--header "X-Auth: $${TOKEN}" \
		--data @examples/serviceslometrics.json \
		localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/serviceslometrics/app-sre-prod-01 && \
	curl \
		--request DELETE \
		"localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/token/$${TOKEN}?scope=serviceslometrics"

test-data-deploymentvalidation:
	@TOKEN=$$(curl --silent localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/token?scope=deploymentvalidation | sed 's/"//g') && \
	echo "deploymentvalidation:" && \
	curl \
		-X POST \
		--header "Content-Type: application/json" \
		--header "X-Auth: $${TOKEN}" \
		--data @examples/deploymentvalidation.json \
		localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/deploymentvalidation/app-sre-prod-01 && \
	curl \
		--request DELETE \
		"localhost:$(DASHDOTDB_FLASK_PORT)/api/v1/token/$${TOKEN}?scope=deploymentvalidation"

test-data: test-data-imagemanifestvuln test-data-serviceslometrics test-data-deploymentvalidation
	

.PHONY: help
help:
	echo "CONTAINER_ENGINE=$(CONTAINER_ENGINE)"
