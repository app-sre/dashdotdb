-include Makefile.devhelpers

clean:
	rm -rf venv
	python3 -m venv venv


install: clean
	. venv/bin/activate && \
	python3 setup.py install


install-requirements: install
	. venv/bin/activate && \
	pip3 install -r requirements-check.txt --user


develop: clean
	. venv/bin/activate && \
	python3 setup.py develop && \
	pip3 install -r requirements-check.txt --user


check:
	. venv/bin/activate && \
	flake8 dashdotdb && \
	pylint dashdotdb
