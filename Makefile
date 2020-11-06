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
	pylint dashdotdb
