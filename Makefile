-include Makefile.devhelpers

CONTAINER_ENGINE ?= $(shell which podman docker | head -n 1) 
ifeq (,$(wildcard $(CONTAINER_ENGINE)))
$(error Couldn't find a container engine (podman or docker) in $$PATH)
endif
LDFLAGS ?= "-I/opt/homebrew/opt/openssl/include -L/opt/homebrew/opt/openssl/lib"

.PHONY: clean
clean: pyproject.toml
	rm -rf .venv

.venv:
	env LDFLAGS=$(LDFLAGS) \
	uv -v sync

.PHONY: sync
sync: .venv

.PHONY: install
install:
	env LDFLAGS=$(LDFLAGS) \
	uv sync

.PHONY: check
check: flake8 pylint mypy

.PHONY: flake8
flake8: .venv
	env LDFLAGS=$(LDFLAGS) \
	uv run     \
	--isolated \
	flake8     \
	-v         \
	dashdotdb

.PHONY: pylint
pylint: .venv
	env LDFLAGS=$(LDFLAGS) \
	uv run     \
	--isolated \
	pylint     \
	-v         \
	dashdotdb


.PHONY: mypy
mypy: .venv
	env LDFLAGS=$(LDFLAGS) \
	uv -v run         \
	--isolated        \
	mypy              \
	--install-types   \
	--non-interactive \
	--follow-untyped-imports

.PHONY: ci
ci:
	$(CONTAINER_ENGINE) build -t app-sre-dashdotdb-ci:do-not-use --target test -f Dockerfile .
	$(CONTAINER_ENGINE) build -t app-sre-dashdotdb:do-not-use --target prod -f Dockerfile .

test-data:
	$(eval TOKEN := $(shell curl --silent localhost:8080/api/v1/token?scope=imagemanifestvuln | sed 's/"//g'))
	curl -X POST --header "Content-Type: application/json" --header "X-Auth: $(TOKEN)" --data @examples/imagemanifestvuln.json localhost:8080/api/v1/imagemanifestvuln/app-sre-prod-01
	curl --request DELETE "localhost:8080/api/v1/token/$(TOKEN)?scope=imagemanifestvuln"
	$(eval TOKEN := $(shell curl --silent localhost:8080/api/v1/token?scope=serviceslometrics | sed 's/"//g'))
	curl -X POST --header "Content-Type: application/json" --header "X-Auth: $(TOKEN)" --data @examples/serviceslometrics.json localhost:8080/api/v1/serviceslometrics/app-sre-prod-01
	curl --request DELETE "localhost:8080/api/v1/token/$(TOKEN)?scope=serviceslometrics"
	$(eval TOKEN := $(shell curl --silent localhost:8080/api/v1/token?scope=deploymentvalidation | sed 's/"//g'))
	curl -X POST --header "Content-Type: application/json" --header "X-Auth: $(TOKEN)" --data @examples/deploymentvalidation.json localhost:8080/api/v1/deploymentvalidation/app-sre-prod-01
	curl --request DELETE "localhost:8080/api/v1/token/$(TOKEN)?scope=deploymentvalidation"

.PHONY: help
help:
	@echo "CONTAINER_ENGINE=$(CONTAINER_ENGINE)"
	@echo "LDFLAGS=$(LDFLAGS)"
	@echo "You may need to change LDFLAGS based on your own system to get OpenSSL to link properly."
	@echo "In this case, you can use: make LDFLAGS=\"....\" sync", or any other target.