SHELL := /usr/bin/env bash

# Want to skip this check? make CONTAINER_ENGINE=skip <target>
# It can be anything, but bear in mind that commands want to be run with that first
CONTAINER_ENGINE ?= $(shell which -a podman docker | head -n 1) 
ifndef CONTAINER_ENGINE
$(error CONTAINER_ENGINE is unset because it couldn't be auto-set; podman or docker missing from $$PATH. Skip this check with make CONTAINER_ENGINE=skip; but container commands will not work)
endif

# Don't want uv to use its local cache?
# make IGNORE_UV_CACHE_FLAG=-n <target>
IGNORE_UV_CACHE_FLAG ?= 

# Use an isolated UV environment?
UV_USE_ISOLATED ?= yes
__UV_USE_ISOLATED :=
ifeq ($(UV_USE_ISOLATED),yes)
	__UV_USE_ISOLATED := --isolated
endif


-include Makefile.devhelpers

# Attempt to auto set LDFLAGS
# MacOS needs to use homebrew to install openssl and then use these LDFLAGS.
# But, Linux typically doesn't need to change them, so don't. No idea what to do
# for Windows
# Note: This is likely not needed with Python 3.11 and beyond.
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	LDFLAGS ?= "-I/opt/homebrew/opt/openssl/include -L/opt/homebrew/opt/openssl/lib"
endif

.PHONY: clean
clean: pyproject.toml
	rm -rf .venv
	if [[ "xskip" != "x$${CONTAINER_ENGINE}" ]]; then \
		$(CONTAINER_ENGINE) rmi app-sre-dashdotdb-ci:do-not-use app-sre-dashdotdb:do-not-use 2>/dev/null || true ;\
	fi

.venv:
	@if [[ "xDarwin" == "x$(UNAME_S)" ]]; then \
		export LDFLAGS=$(LDFLAGS) ;\
	fi &&                 \
	uv sync               \
	--no-group dev        \
	$(IGNORE_UV_CACHE_FLAG)

.PHONY: sync
sync: .venv pyproject.toml

.PHONY: install
install:
	@if [[ "xDarwin" == "x$(UNAME_S)" ]]; then \
		export  LDFLAGS=$(LDFLAGS) ;\
	fi && \
	uv sync \
	$(IGNORE_UV_CACHE_FLAG)

.PHONY: check
check: flake8 pylint mypy

.PHONY: flake8
flake8:
	@if [[ "xDarwin" == "x$(UNAME_S)" ]]; then \
		export LDFLAGS=$(LDFLAGS) ;\
	fi && \
	uv run $(__UV_USE_ISOLATED) \
	--frozen                    \
	--active                    \
	--group dev                 \
	$(IGNORE_UV_CACHE_FLAG)     \
		flake8                    \
		dashdotdb

.PHONY: pylint
pylint:
	@if [[ "xDarwin" == "x$(UNAME_S)" ]]; then \
		export LDFLAGS=$(LDFLAGS) ;\
	fi && \
	uv run $(__UV_USE_ISOLATED) \
	--frozen                    \
	--active                    \
	--group dev                 \
	$(IGNORE_UV_CACHE_FLAG)     \
		pylint                    \
			dashdotdb


.PHONY: mypy
mypy:
	@if [[ "xDarwin" == "x$(UNAME_S)" ]]; then \
		export LDFLAGS=$(LDFLAGS) ;\
	fi && \
	uv run $(__UV_USE_ISOLATED) \
	--frozen                    \
	--active                    \
	--group dev                 \
	$(IGNORE_UV_CACHE_FLAG)     \
		mypy                      \
			--install-types         \
			--non-interactive       \
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
	@if [[ "xDarwin" == "x$(UNAME_S)" ]]; then \
		export LDFLAGS=$(LDFLAGS) ;\
	fi && \
	echo "CONTAINER_ENGINE=$(CONTAINER_ENGINE)" && \
	echo "Makefile LDFLAGS=$(LDFLAGS)" && \
	echo "UNAME_S=$(UNAME_S)" && \
	echo "Shell thinks LDFLAGS=$${LDFLAGS}" && \
	echo "Isolated environments? UV_USE_ISOLATED=$(UV_USE_ISOLATED). Flag=$(__UV_USE_ISOLATED)"
	echo "You may need to change LDFLAGS based on your own system to get OpenSSL to link properly." && \
	echo "In this case, you can use: make LDFLAGS=\"....\" <make target>".

