-include Makefile.devhelpers

clean:
	rm -rf venv
	python3 -m venv venv


install: clean
	. venv/bin/activate && \
	python setup.py install


install-requirements: install
	. venv/bin/activate && \
	pip install -r requirements-check.txt


develop: clean
	. venv/bin/activate && \
	python setup.py develop && \
	pip install -r requirements-check.txt 


check:
	. venv/bin/activate && \
	flake8 dashdotdb && \
	mypy --install-types --non-interactive && \
	pylint dashdotdb

ci:
	docker build -t app-sre-dashdotdb-ci:do-not-use -f Dockerfile.ci .
	docker build -t app-sre-dashdotdb:do-not-use .

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
